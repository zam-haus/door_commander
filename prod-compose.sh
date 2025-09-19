#!/bin/bash
set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"
. ./secrets.env
$COMPOSE "$@"