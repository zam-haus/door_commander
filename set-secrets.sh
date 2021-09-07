#!/bin/bash
set -euf -o pipefail
# set -x

# stop and remove all containers, otherwise we can't pass the new parameters as environment variables
docker-compose down

source .env

# clear the file
echo >secrets.env

# helper function, uses 256bit of entropy
generate_password() { head -c32 /dev/random | base64; }





# generate all necessary secrets and save them
MQTT_PASSWD_CONTROLLER="$(generate_password)"
export MQTT_PASSWD_CONTROLLER
declare -p MQTT_PASSWD_CONTROLLER >>secrets.env
rm -f mosquitto/config/mosquitto.passwd
touch mosquitto/config/mosquitto.passwd  # otherwise a directory will be created
docker-compose run --rm mqtt mosquitto_passwd -b /mosquitto/config/mosquitto.passwd controller "$MQTT_PASSWD_CONTROLLER"





POSTGRES_PASSWORD="$(generate_password)"
export POSTGRES_PASSWORD
declare -p POSTGRES_PASSWORD >>secrets.env
docker-compose run --rm db /docker-postgres-run-command.sh /update_superuser.sh

POSTGRES_PASSWORD_DJANGO="$(generate_password)"
export POSTGRES_PASSWORD_DJANGO
declare -p POSTGRES_PASSWORD_DJANGO >>secrets.env
USER="${POSTGRES_USER_DJANGO}" PASSWORD="${POSTGRES_PASSWORD_DJANGO}" DB="${POSTGRES_DB_DJANGO}" \
  docker-compose run --rm \
  -e USER -e PASSWORD -e DB \
  db /docker-postgres-run-command.sh /update_other_user.sh






# THIS KEY CONNECTS DOCKER TO GITHUB; IT IS NOT ROTATED AUTOMATICALLY
test -f id_rsa_git || ssh-keygen -t rsa -b 4096 -m pem -f id_rsa_git -N ""
OPAL_GIT_PRIVATE_KEY="$(cat id_rsa_git | tr '\n' '_')"
OPAL_GIT_PUBLIC_KEY="$(cat id_rsa_git.pub)"
echo "Add this key to git:"
echo "$OPAL_GIT_PUBLIC_KEY"
export OPAL_GIT_PRIVATE_KEY
declare -p OPAL_GIT_PRIVATE_KEY >>secrets.env

rm -f id_rsa id_rsa.pub
ssh-keygen -t rsa -b 4096 -m pem -f id_rsa -N ""
OPAL_AUTH_PRIVATE_KEY="$(cat id_rsa | tr '\n' '_')"
OPAL_AUTH_PUBLIC_KEY="$(cat id_rsa.pub)"
export OPAL_AUTH_PRIVATE_KEY
export OPAL_AUTH_PUBLIC_KEY
declare -p OPAL_AUTH_PRIVATE_KEY >>secrets.env
declare -p OPAL_AUTH_PUBLIC_KEY >>secrets.env

OPAL_AUTH_MASTER_TOKEN="$(docker run --rm authorizon/opal-server opal-server generate-secret)"
export OPAL_AUTH_MASTER_TOKEN
declare -p OPAL_AUTH_MASTER_TOKEN >>secrets.env

# the -T disables docker-compose from allocating a TTY, which is necessary if we don't want a \r from CRLF line endings.
# use --no-just-the-token to get an error message if the python code fails with when trying to find data['token']
OPAL_AUTH_CLIENT_TOKEN="$(
  docker-compose run --rm -T opa-sidecar \
    opal-client obtain-token "$OPAL_AUTH_MASTER_TOKEN" \
    --server-url=http://opal-server:7002 --type client
  #--no-just-the-token \
)"
export OPAL_AUTH_CLIENT_TOKEN
declare -p OPAL_AUTH_CLIENT_TOKEN >> secrets.env


echo "TODO: You need to provide OIDC_RP_CLIENT_SECRET manually."
OIDC_RP_CLIENT_SECRET=""
export OIDC_RP_CLIENT_SECRET
declare -p OIDC_RP_CLIENT_SECRET >> secrets.env





echo "Secrets successfully set"
