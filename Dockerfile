ARG PYTHON_VERSION=3.13
ARG NGINX_VERSION=latest
FROM docker.io/python:${PYTHON_VERSION} AS python-dependencies

#RUN apk add --no-cache openssl
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-alpine-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN pip install pipenv

WORKDIR /opt/door-commander.betreiberverein.de/

COPY Pipfile .
#COPY Pipfile.lock .
# We have to enable this to allow the non-root-user to access the write-protected python later on.
# Otherwise, the venv would reside in /root/.local/share/virtualenvs/
ENV PIPENV_VENV_IN_PROJECT=1
# alpine does not support manylinux, and needs to compile psycopg2
RUN pipenv --python 3.13
RUN pipenv install --deploy


FROM python-dependencies AS python-app

COPY src .

# remove all present data, and replace it with the production data
# This should be one of the last steps, to ensure no prepopulated secret gets included in the build.
RUN rm -rf ./data/
RUN mkdir ./data/
COPY src/production-data ./data/



FROM python-app as python-static
RUN COLLECTSTATIC_DIR=/opt/static.door-commander.betreiberverein.de/static pipenv run python manage.py collectstatic
WORKDIR /opt/static.door-commander.betreiberverein.de/
# RUN ls .



FROM docker.io/nginx:${NGINX_VERSION} as nginx
RUN rm /etc/nginx/conf.d/default.conf
# Assert there is no other site configured, e.g. after a base image update
RUN test -n "$(find /etc/nginx/conf.d/ -empty -maxdepth 0)"
ADD nginx/default.conf /etc/nginx/conf.d/default.conf
WORKDIR /var/www/web/
COPY --from=python-static /opt/static.door-commander.betreiberverein.de/static/ ./static/
#RUN pwd ; ls -la ; ls -la static
# no USER directive; nginx will switch to the "nginx" user by itself, as configured by the base image
EXPOSE 80



FROM python-app as python-web
RUN adduser --system app --group
RUN chown app:app data
RUN chmod 700 data
USER app
VOLUME /opt/door-commander.betreiberverein.de/data/

EXPOSE 8000
ENTRYPOINT ["pipenv", "run"]
CMD ["dockerize", "-timeout", "10s", "gunicorn", "door_commander.wsgi"]

