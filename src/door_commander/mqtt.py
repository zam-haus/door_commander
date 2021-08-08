import json
from json import loads
from numbers import Number

from icecream import ic
from paho.mqtt.client import MQTTMessage
from pymaybe import maybe

from mqtt_framework import GenericMqttEndpoint

from door_commander.settings import MQTT_CLIENT_KWARGS, MQTT_SERVER_KWARGS, MQTT_PASSWORD_AUTH, MQTT_TLS


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

    def open(self, mqtt_id, timeout: Number):
        payload = dict(not_after=timeout)
        self.publish("door/+/open", mqtt_id, qos=2, retain=False, payload=json.dumps(payload))


door_commander_mqtt: MqttDoorCommanderEndpoint = None


def start_connection():
    global door_commander_mqtt
    if door_commander_mqtt is None:
        door_commander_mqtt = MqttDoorCommanderEndpoint(
            client_kwargs=MQTT_CLIENT_KWARGS,
            password_auth=MQTT_PASSWORD_AUTH,
            server_kwargs=MQTT_SERVER_KWARGS,
            tls=MQTT_TLS
        )
        door_commander_mqtt.connect()
