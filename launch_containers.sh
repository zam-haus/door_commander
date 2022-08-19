#!/bin/bash
set -euf -o pipefail
COMPOSE="docker-compose -f docker-compose.yml -f docker-compose.prod.yml"

test -f secrets.env
source secrets.env

set -x
$COMPOSE build --parallel
# recreate the containers with the new password.
$COMPOSE up --no-start --force-recreate
$COMPOSE run --rm python ./manage.py check --deploy
$COMPOSE run --rm python ./manage.py migrate
$COMPOSE up
