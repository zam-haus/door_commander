import time


def wait_until(condition, interval=0.1, timeout=1, *args):
    start = time.time()
    while not (result := condition(*args)) and time.time() - start < timeout:
        time.sleep(interval)
    # True if condition fulfilled
    return result
