import json
import threading
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, UTC
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


@dataclass
class CardReadEvent:
    door_mqtt_id: str
    card_secret_id: str
    when: datetime


class MqttCardreaderEndpoint(GenericMqttEndpoint):
    def __init__(self, client_kwargs: dict, password_auth: dict, server_kwargs: dict, tls: bool):
        super().__init__(client_kwargs, password_auth, server_kwargs, tls)

        self._last_card_read: defaultdict[str, CardReadEvent | None] = defaultdict(lambda: None)
        """This is indexed by door mqtt id"""
        self._last_card_read_cv = defaultdict(lambda: threading.Condition())
        """This is indexed by door mqtt id"""

    def get_last_card_read(self, terminal_mqtt_id) -> CardReadEvent | None:
        with (cv := self._last_card_read_cv[terminal_mqtt_id]):
            # publish an empty message to be received after or instead of the retained message
            self.publish("door/+/card_read", terminal_mqtt_id, qos=2, payload="")
            if (event := self._last_card_read[terminal_mqtt_id]):
                return event
            else:
                # Wait one second for a card read event to arrive
                # Ideally the event is retained and will be received shortly after connection and subscription
                if not cv.wait(5):
                    log.warning("No card read event received within 1 second for terminal %s", terminal_mqtt_id)
                # This may return None if no card read event was received
                return self._last_card_read[terminal_mqtt_id]

    @property
    def is_connected(self):
        """This is only informational, please use qos=1 or qos=2 if you require a message to be sent."""
        return self._mqttc.is_connected()

    @GenericMqttEndpoint.subscribe_decorator("door/+/card_read", qos=2)
    def update_presence(self, door_id, *, client, userdata, message: MQTTMessage):
        try:
            with (cv := self._last_card_read_cv[door_id]):
                if not message.payload:
                    # This occurs when the empty message sent upon waiting is received
                    # after having received all / no retained messages with qos=2
                    log.debug("Received empty message for door %s, ignoring", door_id)
                    cv.notify_all()
                parsed_payload = loads(message.payload)
                log.debug("Received card read event for door %s: %s", door_id, parsed_payload)
                self._last_card_read[door_id] = CardReadEvent(
                    door_mqtt_id=door_id,
                    card_secret_id=parsed_payload["card_secret"],
                    when=datetime.fromtimestamp(parsed_payload["when"], UTC),
                )
                cv.notify_all()

            # ic(self._doors_presence)
        except Exception as e:
            log.error(f"Failed to parse card read message: {e}")


def start_connection():
    log.debug(f"Starting MQTT connection {MQTT_SERVER_KWARGS=}, {MQTT_CLIENT_KWARGS=}, {MQTT_TLS=}")
    cardreader_mqtt = MqttCardreaderEndpoint(
        client_kwargs=MQTT_CLIENT_KWARGS,
        password_auth=MQTT_PASSWORD_AUTH,
        server_kwargs=MQTT_SERVER_KWARGS,
        tls=MQTT_TLS
    )
    cardreader_mqtt.connect()
    return cardreader_mqtt


cardreader_mqtt: MqttCardreaderEndpoint = lazy_object_proxy.Proxy(start_connection)
