#!/bin/bash

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

. secrets.env

if [ -z "$1" ] ; then
  echo "Pass the command as \$@"
  exit 1
fi
$COMPOSE run --rm mqtt mosquitto_ctrl -h mqtt -u controller -P "${MQTT_PASSWD_CONTROLLER}" -p 1883 dynsec "$@"



