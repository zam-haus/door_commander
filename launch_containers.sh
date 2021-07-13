#!/bin/bash
set -euf -o pipefail
COMPOSE="docker-compose -f docker-compose.yml"
POSTGRES_PASSWORD="$(head -c32 /dev/random | base64)"
export POSTGRES_PASSWORD
echo "Your database superuser password of the day -- will change upon next launch:"
echo "User: user"
echo "Password: ${POSTGRES_PASSWORD}"
# TODO this will fail to restart
POSTGRES_DJANGO_PASSWORD="$(head -c32 /dev/random | base64)"
export POSTGRES_DJANGO_PASSWORD
$COMPOSE build --parallel
# recreate the containers with the new password.
$COMPOSE up --no-start --force-recreate
$COMPOSE run python ./manage.py check --deploy
$COMPOSE run python ./manage.py migrate
$COMPOSE up
