import json
from ipaddress import ip_address, ip_network
from json import loads
from logging import getLogger
from numbers import Number

from decorated_paho_mqtt import GenericMqttEndpoint, pack_topic
from django.conf import settings
from django.utils.functional import lazy
from icecream import ic
from paho.mqtt.client import MQTTMessage
from pymaybe import maybe

from django.conf import settings
from doors.models import Door
import lazy_object_proxy

MQTT_CLIENT_KWARGS = settings.MQTT_CLIENT_KWARGS
MQTT_SERVER_KWARGS = settings.MQTT_SERVER_KWARGS
MQTT_PASSWORD_AUTH = settings.MQTT_PASSWORD_AUTH
MQTT_TLS = settings.MQTT_TLS

log = getLogger(__name__)


class MqttWifiLocatorEndpoint(GenericMqttEndpoint):
    def __init__(self, client_kwargs: dict, password_auth: dict, server_kwargs: dict, tls: bool):
        super().__init__(client_kwargs, password_auth, server_kwargs, tls)

        self._ip_networks = dict()
        """This is indexed by mqtt id"""

    @property
    def ip_networks(self):
        return self._ip_networks

    @property
    def is_connected(self):
        """This is only informational, please use qos=1 or qos=2 if you require a message to be sent."""
        return self._mqttc.is_connected()

    @GenericMqttEndpoint.subscribe_decorator("locator/+/ip", qos=2)
    # door_id is automatically filled in with the value for the "+" by the decorator
    def update_ip(self, locator_id, *, client, userdata, message: MQTTMessage):
        try:
            # This is faked by paho upon receipt, we could use the current time ourselves just as well.
            #  It will not be able to recognize connection delay.
            locally_faked_timestamp: float = message.timestamp

            topic: str = message.topic
            retained = message.retain
            props = maybe(message.properties).json()
            timestamp = props.timestamp
            parsed_payload = loads(message.payload)
            # door_id, = unpack_topic("door/+/presence", message.topic)

            ips = parsed_payload["ip_addresses"]
            parsed_ip_networks = []
            for ip in ips:
                try:
                    parsed_ip_networks.append(ip_network(ip, strict=False))
                except:
                    log.error("Failed to parse zam ip, thus ignoring entry: "+repr(ip))
            self._ip_networks[locator_id] = parsed_ip_networks
        except Exception as e:
            log.error("Failed to parse door presence message: "+repr(e))

    def open(self, mqtt_id, timeout: Number):
        payload = dict(not_after=timeout)
        self.publish("door/+/open", mqtt_id, qos=2, retain=False, payload=json.dumps(payload))

    def door_name(self, mqtt_id, name):
        topic = pack_topic("door/+/display_name", mqtt_id)
        return self._mqttc.publish(topic, json.dumps(name), qos=2,retain=True)

def start_connection():
    wifi_locator_mqtt = MqttWifiLocatorEndpoint(
        client_kwargs=MQTT_CLIENT_KWARGS,
        password_auth=MQTT_PASSWORD_AUTH,
        server_kwargs=MQTT_SERVER_KWARGS,
        tls=MQTT_TLS
    )
    wifi_locator_mqtt.connect()
    return wifi_locator_mqtt

wifi_locator_mqtt: MqttWifiLocatorEndpoint = lazy_object_proxy.Proxy(start_connection)
