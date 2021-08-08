# SPDX-License-Identifier: MIT
ARG POSTGRES_VERSION=latest
FROM postgres:${POSTGRES_VERSION}

# Check the location where we want to insert our hook is actually there.
#RUN sed '/PostgreSQL Database directory appears to contain a database; Skipping initialization/{q42}' ./docker-entrypoint.sh >/dev/null; \
#    test $? -eq 42 || ("Failed to patch docker-entrypoint.sh to add a pre-start-script"; exit 1)

# TODO this might be worth an upstream pull request to avoid patching dependencies.
# And insert a call to run-parts -- this will run files in /docker-entrypoint-restartdb.d/ whenever the server is restarted after first initialization.
#RUN sed -i '/PostgreSQL Database directory appears to contain a database; Skipping initialization/adocker_temp_server_start "$@" ; run-parts --report docker-entrypoint-restartdb.d ; docker_temp_server_stop' ./docker-entrypoint.sh
#RUN tail -n20 ./docker-entrypoint.sh

#COPY update_superuser update_django_user /docker-entrypoint-restartdb.d/
#RUN chmod go+x /docker-entrypoint-restartdb.d/*

ADD docker-postgres-run-command.sh /
ADD docker-postgres-run-server.sh /
ADD update_superuser.sh /
ADD update_other_user.sh /

CMD ["/docker-postgres-run-server.sh"]
ENTRYPOINT []