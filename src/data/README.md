# Development and Debugging Data
Data in this directory is used for development and debugging.
It is removed when the docker container is build, and replaced by the data in production-data.

If you need to debug on a development docker container, try

    docker-compose exec python touch data/ACTIVATE_DEBUG_MODE