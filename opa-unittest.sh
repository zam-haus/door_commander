#!/bin/bash
set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.debug.yml"
$COMPOSE run --rm opa test /data/policy -v