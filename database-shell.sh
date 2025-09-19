#!/bin/bash
set -euf -o pipefail

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
$COMPOSE exec db psql "$POSTGRES_DB_DJANGO" -U user
