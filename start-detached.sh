#!/usr/bin/env bash
set -euf -o pipefail

test -f secrets.env
source secrets.env

docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --detach
