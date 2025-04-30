#!/usr/bin/env bash
set -euf -o pipefail

test -f secrets.env
source secrets.env



COMPOSE="docker-compose"
which podman-compose && COMPOSE="podman-compose"
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"
$COMPOSE up --detach
