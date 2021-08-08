#!/bin/bash
# The code below is partially copied from
# https://github.com/docker-library/postgres/blob/master/docker-entrypoint.sh
# SPDX-License-Identifier: MIT

set -e
# we cannot set -u if we source docker-entrypoint.sh, they use undefined variables without checking.
source docker-entrypoint.sh

docker_setup_env
# setup data directories and permissions (when run as root)
docker_create_db_directories
if [ "$(id -u)" = '0' ]; then
  # then restart script as postgres user
  exec gosu postgres "$BASH_SOURCE" "$@"
fi

# only run initialization on an empty data directory
if [ -z "$DATABASE_ALREADY_EXISTS" ]; then
  docker_verify_minimum_env

  # check dir permissions to reduce likelihood of half-initialized database
  ls /docker-entrypoint-initdb.d/ >/dev/null

  docker_init_database_dir
  pg_setup_hba_conf

  # PGPASSWORD is required for psql when authentication is required for 'local' connections via pg_hba.conf and is otherwise harmless
  # e.g. when '--auth=md5' or '--auth-local=md5' is used in POSTGRES_INITDB_ARGS
  export PGPASSWORD="${PGPASSWORD:-$POSTGRES_PASSWORD}"
  docker_temp_server_start "$@"

  docker_setup_db
  docker_process_init_files /docker-entrypoint-initdb.d/*

  docker_temp_server_stop
  unset PGPASSWORD

  echo
  echo 'PostgreSQL init process complete; ready for start up.'
  echo
else

  docker_temp_server_start "$@"
  /update_superuser.sh
  docker_temp_server_stop
  unset PGPASSWORD

  echo
  echo 'PostgreSQL Database directory appears to contain a database; Skipping initialization'
  echo
fi

exec postgres "$@"
