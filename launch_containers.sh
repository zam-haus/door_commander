#!/bin/bash
set -euf -o pipefail
COMPOSE="docker-compose -f docker-compose.yml"
POSTGRES_PASSWORD="$(head -c32 /dev/random | base64)"


test -f secrets.env
source secrets.env

$COMPOSE build --parallel
# recreate the containers with the new password.
$COMPOSE up --no-start --force-recreate
$COMPOSE run python ./manage.py check --deploy
$COMPOSE run python ./manage.py migrate
$COMPOSE up
