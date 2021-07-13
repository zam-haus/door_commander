import inspect
from collections import defaultdict
from functools import wraps

from icecream import ic
from logging import getLogger

# Read the docs at https://github.com/eclipse/paho.mqtt.python
#  because eclipse.org has outdated information, which does not include MQTTv5
from paho.mqtt.client import Client as MqttClient, MQTTMessage, MQTTv5, MQTT_CLEAN_START_FIRST_ONLY
from paho.mqtt.properties import Properties
from paho.mqtt.reasoncodes import ReasonCodes
from paho.mqtt.subscribeoptions import SubscribeOptions
from pymaybe import maybe
from json import dumps, loads

log = getLogger(__name__)


class GenericMqttEndpoint:

    def __init__(self, client_kwargs: dict, password_auth: dict, server_kwargs: dict, tls: bool):
        """

        :param client_kwargs: See https://github.com/eclipse/paho.mqtt.python/blob/9c22a9c297c0cdc4e1aac13aa19073e09a822961/src/paho/mqtt/client.py#L517
        :param password_auth: See https://github.com/eclipse/paho.mqtt.python/blob/9c22a9c297c0cdc4e1aac13aa19073e09a822961/src/paho/mqtt/client.py#L1318
        :param server_kwargs: See https://github.com/eclipse/paho.mqtt.python/blob/9c22a9c297c0cdc4e1aac13aa19073e09a822961/src/paho/mqtt/client.py#L913
        :param tls: If true, enables TLS with https://github.com/eclipse/paho.mqtt.python/blob/9c22a9c297c0cdc4e1aac13aa19073e09a822961/src/paho/mqtt/client.py#L765
        """
        self.mqtt_client_kwargs = client_kwargs
        # Some features and parameters depend on this.
        self.mqtt_client_kwargs.update(protocol=MQTTv5)
        self.mqtt_tls = tls
        self.mqtt_password_auth = password_auth
        self.mqtt_server_kwargs = server_kwargs
        # This is specific to MQTTv5 (MQTTv311 has clean_session in the client_kwargs instead)
        self.mqtt_server_kwargs.update(clean_start=MQTT_CLEAN_START_FIRST_ONLY)

        self._mqttc = MqttClient(**self.mqtt_client_kwargs)

        if self.mqtt_tls:
            self._mqttc.tls_set()

        if self.mqtt_password_auth:
            self._mqttc.username_pw_set(**self.mqtt_password_auth)

        self._mqttc.on_connect = self._on_connect
        self._mqttc.on_disconnect = self._on_disconnect
        self._mqttc.on_message = self._on_message
        self._mqttc.on_log = self._on_log

        self._managed_subsciptions = dict()
        """
        This dictionary maps subscription topics to subscription options
        """

        for attribute in self.__class__.__dict__.values():
            if hasattr(attribute, _SUBSCRIBE_DECORATOR_NAME):
                decorated_function = attribute
                topic_pattern, kwargs = getattr(decorated_function, _SUBSCRIBE_DECORATOR_NAME)

                if topic_pattern in self._managed_subsciptions:
                    raise Exception(
                        "A client cannot subscribe to an identical topic filter multiple times!")
                else:
                    self._managed_subsciptions[topic_pattern] = kwargs

                # This function introduces a scope,
                #  to avoid a changing decorated_function variable
                #  cause changing behaviour of call_decorated_function
                def create_caller(decorated_function):
                    # the decorated_function has not yet a self object; thus we need this wrapper
                    @wraps(decorated_function)
                    def call_decorated_function(client, userdata, message):
                        variables = unpack_topic(topic_pattern, message.topic)
                        return decorated_function(self, client=client, userdata=userdata, message=message, *variables)

                    return call_decorated_function

                # this is done only once, not on every reconnect / resubscribe.
                self._mqttc.message_callback_add(topic_pattern, create_caller(decorated_function))

    def connect(self):
        # currently, this will retry first connects, we don't need bettermqtt
        self._mqttc.connect_async(**self.mqtt_server_kwargs)
        self._mqttc.loop_start()

    def _on_connect(self, client, userdata, flags, rc: ReasonCodes, properties: Properties = None):
        ic("connect", client, userdata, flags, rc.json(), properties.json())
        if flags['session present'] == 0:
            # This is a new session, and we need to resubscribe
            self._subscribe()
        elif flags['session present'] == 1:
            pass
        else:
            raise Exception("Unknown Session Present Flag")

    def _subscribe(self):
        # Edge case: This may fail if we disconnect when not subscribed to all channels; there seems to a case where
        #  subscribe() returns an error code that we currently do handle.
        #  With some luck, the subscription stays in the packet queue.

        # Other defaults are sane, we don't need Subscription Options

        # However, if our session expires (after long-lasting conection loss),
        #  we will unexpectedly re-receive all retained messages
        #  which is not bad, if they are idempotent

        # We MUST NOT add message callbacks here, otherwise, they may be added twice upon reconnect after session expiry
        for topic_filter, kwargs in self._managed_subsciptions.items():
            self._mqttc.subscribe(topic=topic_filter, **kwargs)

    def _on_disconnect(self, client, userdata, rc: ReasonCodes, properties: Properties = None):
        # Exceptions here seem to disrupt the automatic reconnect
        # Connection loss can be tested with:
        # sudo tc qdisc add dev lo root netem loss 100%
        # sudo tc qdisc del dev lo root
        ic("disconnect", client, userdata, rc, maybe(properties).json())

    def _on_message(self, client, userdata, message: MQTTMessage):
        message_dict = {attr: getattr(message, attr) for attr in dir(message) if not attr.startswith("_")}
        message_properties: Properties = message.properties
        message_properties_dict = {attr: getattr(message_properties, attr) for attr in dir(message_properties) if
                                   not attr.startswith("_")}
        # ic("message", client, userdata, message_dict, message_properties.json())

    def _on_log(self, client, userdata, level, buf):
        log.log(level, buf, extra=dict(userdata=userdata))
        # ic("log", client, userdata, level, buf)

    @staticmethod
    def subscribe_decorator(topic, **kwargs):
        """
        This must be the outermost decorator (except for other similar nop-decorators)

        Avoid overlapping subscriptions or handle duplicates.
        Uses the same kwargs as paho.mqtt.client.Client.subscribe()
        Try qos=2 or options=SubscriptionOptions()

        Your function should have the signature func(var1, var2, vars, *, client,userdata,message)
        with a positional variable for each + or # in the pattern
        """

        def _subscribe_decorator(func):
            setattr(func, _SUBSCRIBE_DECORATOR_NAME, (topic, kwargs))
            # no @wraps
            return func

        return _subscribe_decorator


_SUBSCRIBE_DECORATOR_NAME = name = __name__ + "." + GenericMqttEndpoint.subscribe_decorator.__qualname__


def unpack_topic(pattern, topic):
    """
    returns one string for each "+", followed by a list of strings when a trailing "#" is present
    """
    pattern_parts = iter(pattern.split("/"))
    topic_parts = iter(topic.split("/"))
    while True:
        try:
            cur_pattern = next(pattern_parts)
        except StopIteration:
            try:
                cur_topic = next(topic_parts)
                raise Exception("The topic to be matched is longer than the pattern without an # suffix. "
                                "The first unmatched part is {!r}".format(cur_topic))
            except StopIteration:
                # no more elements in both sequences.
                return
        if cur_pattern == "#":
            yield list(topic_parts)
            try:
                cur_pattern = next(pattern_parts)
                raise Exception("The pattern has a component after a #: {!r}".format(cur_pattern))
            except StopIteration:
                # topic has been exhausted by list() enumeration, and pattern is empty, too.
                return
        else:
            try:
                cur_topic = next(topic_parts)
            except StopIteration:
                raise Exception("The topic lacks a component to match a non-#-component in the pattern.")
            else:
                if cur_pattern == "+":
                    yield cur_topic
                elif "+" in cur_pattern:
                    raise Exception(
                        "The single-level wildcard can be used at any level in the Topic Filter, including first and last levels. Where it is used, it MUST occupy an entire level of the filter.")
                elif "#" in cur_pattern:
                    raise Exception(
                        "The multi-level wildcard character MUST be specified either on its own or following a topic level separator. In either case it MUST be the last character specified in the Topic Filter.")
                elif cur_pattern != cur_topic:
                    raise Exception(
                        "The pattern {!r} is no wildcard, and the topic {!r} differs.".format(cur_pattern, cur_topic))
                else:  # pattern == topic and neither contain a # or +
                    # we do not yield return constant non-wildcards.
                    continue


class MqttDoorCommanderEndpoint(GenericMqttEndpoint):
    def __init__(self, client_kwargs: dict, password_auth: dict, server_kwargs: dict, tls: bool):
        super().__init__(client_kwargs, password_auth, server_kwargs, tls)

        self.doors_presence = dict()

    @property
    def is_connected(self):
        """This is only informational, please use qos=1 or qos=2 if you require a message to be sent."""
        return self._mqttc.is_connected()

    @GenericMqttEndpoint.subscribe_decorator("door/+/presence", qos=2)
    # door_id is automatically filled in with the value for the "+" by the decorator
    def update_presence(self, door_id, *, client, userdata, message: MQTTMessage):
        # This is faked by paho upon receipt, we could use the current time ourselves just as well.
        #  It will not be able to recognize connection delay.
        locally_faked_timestamp: float = message.timestamp

        topic: str = message.topic
        retained = message.retain
        props = maybe(message.properties).json()
        timestamp = props.timestamp
        parsed_payload = loads(message.payload)
        # door_id, = unpack_topic("door/+/presence", message.topic)
        ic(topic,
           props,
           locally_faked_timestamp,
           timestamp,
           retained,
           message.payload,
           parsed_payload,
           door_id)


        self.doors_presence[door_id] = bool(parsed_payload)

        ic(self.doors_presence)
