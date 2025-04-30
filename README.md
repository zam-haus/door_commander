# Wichtiges zur Nutzung

./set-secrets.sh löscht secrets an lustigen Stellen - NICHT in einem schon konfigurierten Umfeld nutzen, sonst ist alles kaputt:

 * Türenzugangsdaten werden in der mosquitto.passwd gelöscht


# Alte "Readme"


1. Add the hostname 
   1. in settings.py to ALLOWED_HOSTS
   2. in nginx.conf to server_name
2. ./set-secrets.sh
3. ./create-superuser.sh
4. ./launch-containers.sh
5. Login to http://127.0.0.1:80
6. Open the admin interface
7. Create a door
8. Start ./mqtt_dump_all_messages.sh in a separate terminal
9. Open the application home page
10. Click the button
11. Watch the listener receiving the mqtt message
12. You can update a door's status with the following command (fill in your door's mqtt id)

    ```(. secrets.env ; mosquitto_pub -h localhost -u controller -P "${MQTT_PASSWD_CONTROLLER}" -p 1883 -d -t 'door/f16f33d2-7d87-45d3-937d-f5d64d957e8f/presence' -m 'true')```

# Development with pycharm
You need to set some environment variables in the run configuration:

```PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=door_commander.settings;ACTIVATE_DEBUG_MODE=active;OPA_URL=http://localhost:8181/```

See also the .env loaded by pipenv run and debug.sh