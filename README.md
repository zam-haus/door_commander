1. ./set-secrets.sh
2. ./create-superuser.sh
3. ./launch-containers.sh
4. Login to http://127.0.0.1:80
5. Open the admin interface
6. Create a door
7. Start ./mqtt_dump_all_messages.sh in a separate terminal
8. Open the application home page
9. Click the button
10. Watch the listener receiving the mqtt message
11. You can update a door's status with the following command (fill in your door's mqtt id)

    ```(. secrets.env ; mosquitto_pub -h localhost -u controller -P "${MQTT_PASSWD_CONTROLLER}" -p 1883 -d -t 'door/f16f33d2-7d87-45d3-937d-f5d64d957e8f/presence' -m 'true')```