#!/usr/bin/env bash
set +eux
echo "==== ENABLING DEBUG MODE! DO NOT USE ON PRODUCTION SERVER ===="
export ACTIVATE_DEBUG_MODE=active

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.debug.yml"
. ./secrets.env
$COMPOSE up opa db &
(cd src; pipenv run ./manage.py runserver)

