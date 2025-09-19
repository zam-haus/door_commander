#!/bin/bash
set -euxf -o pipefail

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

test -f secrets.env
source secrets.env
. .env

$COMPOSE build --parallel db
# recreate the containers with the new password.
$COMPOSE up --no-start --force-recreate db
$COMPOSE up db -d
sleep 5
true | $COMPOSE exec -T db dropdb "$POSTGRES_DB_DJANGO" -U user || true
true | ./set-secrets.sh
$COMPOSE up db -d
sleep 5
$COMPOSE exec -T db psql -X "$POSTGRES_DB_DJANGO" -U user
