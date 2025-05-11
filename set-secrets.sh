#!/bin/bash
set -euf -o pipefail
# set -x


test -f secrets.env && (echo "Please delete secrets.env and rerun." && exit 1)

# stop and remove all containers, otherwise we can't pass the new parameters as environment variables
docker-compose down

set -o allexport; source .env; set +o allexport
COMPOSE="$COMPOSE -f docker-compose.yml -f docker-compose.prod.yml"

# clear the file
echo >secrets.env

# helper function, uses 256bit of entropy
generate_password() { head -c32 /dev/random | base64; }





echo ::group::MQTT Django Password
# generate all necessary secrets and save them
MQTT_PASSWD_CONTROLLER="$(generate_password)"
export MQTT_PASSWD_CONTROLLER
declare -p MQTT_PASSWD_CONTROLLER >>secrets.env
rm -f mosquitto/config/mosquitto.passwd
touch mosquitto/config/mosquitto.passwd  # otherwise a directory will be created
$COMPOSE run --rm mqtt mosquitto_passwd -b /mosquitto/config/mosquitto.passwd controller "$MQTT_PASSWD_CONTROLLER"
echo ::endgroup::




echo ::group::pgSQL Superuser Password
POSTGRES_PASSWORD="$(generate_password)"
export POSTGRES_PASSWORD
declare -p POSTGRES_PASSWORD >>secrets.env
$COMPOSE run --rm db /docker-postgres-run-command.sh /update_superuser.sh
echo ::endgroup::

echo ::group::pgSQL Django Password
POSTGRES_PASSWORD_DJANGO="$(generate_password)"
export POSTGRES_PASSWORD_DJANGO
declare -p POSTGRES_PASSWORD_DJANGO >>secrets.env
USER="${POSTGRES_USER_DJANGO}" PASSWORD="${POSTGRES_PASSWORD_DJANGO}" DB="${POSTGRES_DB_DJANGO}" \
  $COMPOSE run --rm \
  -e USER -e PASSWORD -e DB \
  db /docker-postgres-run-command.sh /update_other_user.sh
echo ::endgroup::





echo ::group::OPA Bearer Token
OPA_BEARER_TOKEN="$(generate_password)"
export OPA_BEARER_TOKEN
declare -p OPA_BEARER_TOKEN >>secrets.env
echo ::endgroup::



echo "TODO: You need to provide OIDC_RP_CLIENT_SECRET manually."
OIDC_RP_CLIENT_SECRET=""
export OIDC_RP_CLIENT_SECRET
declare -p OIDC_RP_CLIENT_SECRET >> secrets.env





echo "Secrets successfully set"
