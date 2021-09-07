from .celery import app
import logging

log = logging.getLogger(__name__)


@app.task(bind=True)
def debug_task(self):
    log.debug(f'Request: {self.request!r}')
