#!/bin/bash
set -euf -o pipefail

COMPOSE="docker-compose"
which podman-compose && COMPOSE="podman-compose"
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

test -f secrets.env
source secrets.env

set -x
if which podman-compose ; then
  $COMPOSE build
else
  $COMPOSE build --parallel
fi
# recreate the containers with the new password.
$COMPOSE up --no-start --force-recreate
$COMPOSE run --rm python ./manage.py check --deploy
$COMPOSE run --rm python ./manage.py migrate
$COMPOSE up -d
