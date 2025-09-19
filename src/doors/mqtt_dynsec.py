import json
import threading
from dataclasses import dataclass, field
from json import loads
import logging

from decorated_paho_mqtt import GenericMqttEndpoint, pack_topic
from paho.mqtt.client import MQTTMessage
from doors.models import RemoteClient

from django.conf import settings
from doors.models import Door
import lazy_object_proxy

from wait_until import wait_until

CV_WAIT_TIMEOUT = 10

MQTT_CLIENT_KWARGS = settings.MQTT_CLIENT_KWARGS
MQTT_SERVER_KWARGS = settings.MQTT_SERVER_KWARGS
MQTT_PASSWORD_AUTH = settings.MQTT_PASSWORD_AUTH
MQTT_TLS = settings.MQTT_TLS

log = logging.getLogger(__name__)


@dataclass
class DynSecAcl:
    acltype: str
    """
    Where acltype is one of 
        publishClientSend, publishClientReceive,
        subscribeLiteral, subscribePattern,
        unsubscribeLiteral, and unsubscribePattern.
    """
    topic: str
    priority: int = field(default=0)
    allow: bool = field(default=True)


def prepare_acls(mqtt_id) -> list[DynSecAcl]:
    return [
        DynSecAcl(acltype="subscribePattern", topic=pack_topic("door/+/", mqtt_id) + "#", ),
        DynSecAcl(acltype="publishClientSend", topic=pack_topic("door/+/presence", mqtt_id), ),
        DynSecAcl(acltype="publishClientSend", topic=pack_topic("door/+/open/confirm", mqtt_id), ),
        DynSecAcl(acltype="publishClientSend", topic=pack_topic("door/+/card_read", mqtt_id), ),
        DynSecAcl(acltype="publishClientSend", topic=pack_topic("locator/+/", mqtt_id) + "#", ),
    ]


class MqttAdminEndpoint(GenericMqttEndpoint):
    def __init__(self, client_kwargs: dict, password_auth: dict, server_kwargs: dict, tls: bool):
        super().__init__(client_kwargs, password_auth, server_kwargs, tls)
        self._cv = threading.Condition()
        self.last_responses = None

    @property
    def is_connected(self):
        """This is only informational, please use qos=1 or qos=2 if you require a message to be sent."""
        return self._mqttc.is_connected()

    @GenericMqttEndpoint.subscribe_decorator("$CONTROL/dynamic-security/v1/response", qos=2)
    def dynsec_response_callback(self, *, client, userdata, message: MQTTMessage):
        try:
            log.debug(f"Received response, waiting for lock...")
            with self._cv:
                log.debug("Lock acquired")
                # ic(message)
                # ic(message.payload)
                data = loads(message.payload)
                match data:
                    case {"responses": commands}:
                        self.last_responses = commands
                        self._cv.notify_all()
                        for command in commands:
                            match command:
                                case {"command": command_name, "error": error}:
                                    log.warning(f"Error executing command {command_name!r}: {error!r}")
                                case {"command": command_name}:
                                    log.debug(f"Executed command {command_name!r}")
                                case {"command": command_name, "data": data}:
                                    log.debug(f"Executed command {command_name!r}, returned data {data}")
        except Exception as e:
            log.error(f"Failed to parse message: {e}")

    def set_client(self, username, password, allow_mqtt_ids):
        if not wait_until(lambda: self.is_connected, timeout=5):
            raise Exception("Not connected to MQTT server")

        usernames, roles = self.get_clients_and_roles()

        payload = dict(
            commands=
            [
                dict(
                    command="createRole" if mqtt_id not in roles else "modifyRole",
                    rolename=mqtt_id,
                    textname=mqtt_id,
                    acls=[acl.__dict__ for acl in prepare_acls(mqtt_id)]
                )
                for mqtt_id in allow_mqtt_ids
            ] + [
                dict(
                    command="createClient" if username not in usernames else "modifyClient",
                    username=username,
                    password=password,
                    textname=username,
                    roles=[dict(rolename=mqtt_id, priority=0) for mqtt_id in allow_mqtt_ids],
                )
            ])
        self.tranceive_request(payload)

    def cleanup_clients(self, allowed_usernames, allowed_mqtt_ids):
        if not wait_until(lambda: self.is_connected, timeout=5):
            raise Exception("Not connected to MQTT server")

        allowed_usernames = set(allowed_usernames)
        allowed_mqtt_ids = set(allowed_mqtt_ids)

        client_usernames, role_names = self.get_clients_and_roles()
        surplus_role_names = role_names.difference(allowed_mqtt_ids)
        surplus_client_usernames = client_usernames.difference(allowed_usernames)
        if surplus_role_names:
            log.info(f"Cleaning up roles: {surplus_role_names}")
            for surplus_role_name in surplus_role_names:
                self.remove_role(surplus_role_name)
        if surplus_client_usernames:
            log.info(f"Cleaning up clients: {surplus_client_usernames}")
            for surplus_client_username in surplus_client_usernames:
                self.remove_client(surplus_client_username)

    def get_clients_and_roles(self):

        payload = dict(
            commands=
            [
                dict(
                    command="listClients",
                    verbose=False,
                    count=-1,  # All
                    offset=0,
                ),
                dict(
                    command="listRoles",
                    verbose=False,
                    count=-1,  # All
                    offset=0,
                ),
            ]
        )
        last_responses = self.tranceive_request(payload)

        client_usernames = set()
        role_names = set()

        for command in last_responses:
            match command:
                case {"command": "listClients", "data": {"clients": client_usernames, "totalCount": _}}:
                    client_usernames = set(client_usernames)
                    # ic(client_usernames)

        for command in last_responses:
            match command:
                case {"command": "listRoles", "data": {"roles": role_names, "totalCount": _}}:
                    role_names = set(role_names)
                    # ic(role_names)

        return client_usernames, role_names

    def remove_client(self, username):
        with self._cv:
            payload = dict(
                commands=
                [
                    dict(
                        command="deleteClient",
                        username=username,
                    )
                ]
            )
            self.tranceive_request(payload)

    def remove_role(self, rolename):
        payload = dict(
            commands=
            [
                dict(
                    command="deleteRole",
                    rolename=rolename,
                )
            ]
        )
        self.tranceive_request(payload)

    def tranceive_request(self, payload):
        with self._cv:
            pub = self._mqttc.publish("$CONTROL/dynamic-security/v1", qos=2, retain=False, payload=json.dumps(payload))
            # pub.wait_for_publish()
            log.debug(f"Waiting for response...")
            if not self._cv.wait(CV_WAIT_TIMEOUT):
                raise Exception("Timed out waiting for MQTT response. Was the message to large?")
            return self.last_responses


def start_connection():
    log.debug(f"Starting MQTT connection {MQTT_SERVER_KWARGS=}, {MQTT_CLIENT_KWARGS=}, {MQTT_TLS=}")
    door_commander_mqtt = MqttAdminEndpoint(
        client_kwargs=MQTT_CLIENT_KWARGS,
        password_auth=MQTT_PASSWORD_AUTH,
        server_kwargs=MQTT_SERVER_KWARGS,
        tls=MQTT_TLS
    )
    door_commander_mqtt.connect()
    return door_commander_mqtt


admin_mqtt: MqttAdminEndpoint = lazy_object_proxy.Proxy(start_connection)


def update_mqtt_dynamic_security():
    for rclient in RemoteClient.objects.all():
        update_mqtt_client(rclient)
    cleanup_all_clients_and_roles()


def cleanup_all_clients_and_roles():
    allowed_usernames = [rclient.username for rclient in RemoteClient.objects.all()] \
                        + ["controller"]
    allowed_rolenames = [door.mqtt_id for door in Door.objects.all()] \
                        + ["admin"]
    admin_mqtt.cleanup_clients(allowed_usernames=allowed_usernames, allowed_mqtt_ids=allowed_rolenames)


def update_mqtt_client(rclient):
    log.info(f"updating mqtt client {rclient.id!r}")
    pub = admin_mqtt.set_client(
        username=rclient.username, password=rclient.token,
        allow_mqtt_ids=[door.mqtt_id for door in rclient.doors.all()],
    )
