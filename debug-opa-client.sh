#!/usr/bin/env bash
set +eux
echo "==== THIS REQUIRES debug.sh RUNNING IN PARALLEL ===="

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.debug.yml"
. ./secrets.env
echo "Go to http://127.0.0.1:8182/v1/data to see the loaded bundles."
$COMPOSE up opa-client-prototype

