#!/usr/bin/env bash
set +eux

export ACTIVATE_DEBUG_MODE=active

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.debug.yml"
. ./secrets.env
$COMPOSE up opa db mqtt openldap -d
# Listen on 0.0.0.0 to allow access from inside docker container to this python instance.
if [[ "$1" == "migrate" ]]; then
  echo "Careful, don't migrate the db with this command as it will create objects with the wrong owner. Use ./prod-manage.sh migrate instead."
  exit 1
fi
# Check with `select * from pg_tables;`
(cd src; pipenv run ./manage.py "$@")

