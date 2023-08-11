#!/usr/bin/env bash
set -eu


generate_password() { head -c32 /dev/random | base64; }


if [ $# -eq 0 ]
  then
    echo "No arguments supplied, provide uuid as parameter"
    exit 1
fi


# generate all necessary secrets and save them
MQTT_PASSWD="$(generate_password)"
export MQTT_PASSWD
echo "Username: $1"
echo "Password: $MQTT_PASSWD"
docker-compose run --rm mqtt mosquitto_passwd -b /mosquitto/config/mosquitto.passwd "$1" "$MQTT_PASSWD"
