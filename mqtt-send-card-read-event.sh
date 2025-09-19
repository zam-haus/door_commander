#!/bin/bash

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

. secrets.env

if [ -z "$1" ] ; then
  echo "Pass the door / terminal mqtt id as \$1"
  echo "Ensure that the string is mqtt topic escaped."
  exit 1
fi
if [ -z "$2" ] ; then
  echo "Pass the card secret id as \$2"
  echo "Ensure that the string is json escaped."
  exit 1
fi
echo "{\"card_secret\":\"$2\",\"when\":$(date +%s)}" | ./mqtt-send-message-retained.sh "door/$1/card_read"


