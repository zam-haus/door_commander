#!/bin/bash
# SPDX-License-Identifier: MIT
set -eu
# we cannot set -u if we source docker-entrypoint.sh, they use undefined variables without checking.

echo "Updating your superuser password from your current .env file"
# Set NO_POSTGRESQL_PASSWORD_UPDATE=1 if this is too slow and undo this on every password change.
psql \
  --set=pwd="${POSTGRES_PASSWORD}" \
  --set=user="${POSTGRES_USER}" \
  -U "${POSTGRES_USER}" "${POSTGRES_DB}" <<-HEREDOC
    ALTER USER :"user" WITH PASSWORD :'pwd'
HEREDOC
echo "Password update done."
