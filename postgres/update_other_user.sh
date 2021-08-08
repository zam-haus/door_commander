#!/bin/bash
# SPDX-License-Identifier: MIT

set -eu

echo "Updating your superuser password from your current .env file"

# We cannot use DO $$ BEGIN IF NOT EXSISTS ... END $$ here, because our variables would not be interpreted inside the string.

# if $USER exists as a role
if {
  {
    psql -tA \
      --set=pwd="${PASSWORD}" \
      --set=user="${USER}" \
      -U "${POSTGRES_USER}" "${POSTGRES_DB}" <<-'HEREDOC'
SELECT 1 FROM pg_roles WHERE rolname=:'user'
HEREDOC
  } | grep -q 1
}; then
  echo "User already exists."
  psql \
    --set=pwd="${PASSWORD}" \
    --set=user="${USER}" \
    -U "${POSTGRES_USER}" "${POSTGRES_DB}" <<-'HEREDOC'
  ALTER USER :"user" WITH PASSWORD :'pwd';
HEREDOC
  echo "Password update done."
else
  echo "User does not exist."
  psql \
    --set=pwd="${PASSWORD}" \
    --set=user="${USER}" \
    -U "${POSTGRES_USER}" "${POSTGRES_DB}" <<-'HEREDOC'
  CREATE ROLE :"user" LOGIN PASSWORD :'pwd';
HEREDOC
  echo "User created, password set."
fi

psql \
  --set=db="${DB}" \
  -U "${POSTGRES_USER}" "${POSTGRES_DB}" <<-'HEREDOC'
CREATE DATABASE  :"db" ;
;
HEREDOC
echo "Database created, if not already present."

psql \
  --set=db="${DB}" \
  --set=user="${USER}" \
  -U "${POSTGRES_USER}" "${POSTGRES_DB}" <<-'HEREDOC'
GRANT ALL PRIVILEGES ON DATABASE  :"db"  TO  :"user" ;
;
HEREDOC
echo "Permissions granted, if not already present."
