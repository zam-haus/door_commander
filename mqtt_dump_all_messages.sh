#!/bin/bash

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

. secrets.env

export TOPIC='#'
if [ ! -z "$1" ] ; then
  export TOPIC="$1"
fi
$COMPOSE run --rm mqtt mosquitto_sub -h mqtt -u controller -P "${MQTT_PASSWD_CONTROLLER}" -p 1883 -t "$TOPIC" -v



