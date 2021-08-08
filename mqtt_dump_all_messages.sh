#!/bin/bash
. secrets.env
mosquitto_sub -h localhost -u controller -P "${MQTT_PASSWD_CONTROLLER}" -p 1883 -t "#" -v -d


