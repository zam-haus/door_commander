"""
WSGI config for wissenslandkarte project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from . import assert_database_password
from .mqtt import MqttDoorCommanderEndpoint

from .settings import MQTT_CLIENT_KWARGS, MQTT_SERVER_KWARGS, MQTT_PASSWORD_AUTH, MQTT_TLS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'door_commander.settings')

application = get_wsgi_application()

door_commander_mqtt = MqttDoorCommanderEndpoint(
    client_kwargs=MQTT_CLIENT_KWARGS,
    password_auth=MQTT_PASSWORD_AUTH,
    server_kwargs=MQTT_SERVER_KWARGS,
    tls=MQTT_TLS
)




door_commander_mqtt.connect()