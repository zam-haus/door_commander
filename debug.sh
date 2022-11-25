#!/usr/bin/env bash
set +eux
echo "==== PERMANENTLY ENABLING DEBUG MODE! DO NOT USE ON PRODUCTION SERVER ===="
touch src/data/ACTIVATE_DEBUG_MODE
. ./secrets.env
docker-compose -f docker-compose.yml -f docker-compose.debug.yml up opa db mqtt &
(cd src; pipenv run ./manage.py runserver)

