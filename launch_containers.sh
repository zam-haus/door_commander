#!/bin/bash
set -euf -o pipefail

COMPOSE="docker compose"
which podman-compose && COMPOSE="podman-compose"
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

test -f secrets.env
source secrets.env

set -x
echo "======== Building ========"
if which podman-compose ; then
  $COMPOSE build
else
  $COMPOSE build --parallel
fi
# recreate the containers with the new password.
echo "======== Recreating Containers ========"
$COMPOSE up --no-start --force-recreate
echo "======== Checking Django Deployment ========"
$COMPOSE run --rm python ./manage.py check --deploy
echo "======== Migrating Django Database ========"
$COMPOSE run --rm python ./manage.py migrate
echo "======== Starting Services ========"
$COMPOSE up -d
