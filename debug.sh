#!/usr/bin/env bash
set +eux
echo "==== ENABLING DEBUG MODE! DO NOT USE ON PRODUCTION SERVER ===="
export ACTIVATE_DEBUG_MODE=actived
. ./secrets.env
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up opa db &
(cd src; pipenv run ./manage.py runserver)

