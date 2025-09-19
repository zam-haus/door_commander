#!/bin/bash

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

. secrets.env

if [ -z "$1" ] ; then
  echo "Pass the topic as \$1 and the text as stdin"
  exit 1
fi
$COMPOSE run --rm -T mqtt mosquitto_pub -h mqtt -u controller -P "${MQTT_PASSWD_CONTROLLER}" -p 1883 -t "$1" -l



