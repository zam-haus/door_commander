import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
max_requests = 1000
max_requests_jitter = 100


def post_worker_init(worker):
    import clientipaddress.mqtt
    import doors.mqtt
    # start the mqtt connections by querying the lazy objects.
    # the retain messages will be processed a few seconds later asynchronously, we cannot wait for them here.
    clientipaddress.mqtt.wifi_locator_mqtt.__class__
    doors.mqtt.door_commander_mqtt.__class__