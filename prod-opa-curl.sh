#!/usr/bin/env bash
set +eux
echo "==== THIS REQUIRES launch-containers.sh RUNNING IN PARALLEL ====" >&2
echo "pass 'data' or a subpath as \$1" >&2
set -o allexport; source .env; set +o allexport
. ./secrets.env
./prod-compose.sh run --rm python curl "http://opa:8181/v1/$1" -H "Authorization: Bearer $OPA_BEARER_TOKEN" | python3 -m json.tool
