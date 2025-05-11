#!/usr/bin/env bash
set -euf -o pipefail


set -o allexport; source .env; set +o allexport
test -f secrets.env
source secrets.env


COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"
$COMPOSE up --detach
