#!/usr/bin/env bash
set +eux

export ACTIVATE_DEBUG_MODE=active

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"
. ./secrets.env

set -x
echo "======== Building ========"
$COMPOSE build python
echo "======== Running Docker Compose Command ========"
$COMPOSE run --rm python ./manage.py "$@"

