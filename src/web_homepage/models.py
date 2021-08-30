import uuid

from django.contrib import admin
from django.db import models


_PERMISSION_OPEN_DOOR = 'open_door'
_PERMISSION_LOCATION_OVERRIDE = 'assume_correct_location'
_APP_NAME = "web_homepage."

PERMISSION_OPEN_DOOR = _APP_NAME+_PERMISSION_OPEN_DOOR
PERMISSION_LOCATION_OVERRIDE = _APP_NAME+_PERMISSION_LOCATION_OVERRIDE

class Door(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mqtt_id = models.CharField(max_length=256, unique=True, db_index=True)
    display_name = models.TextField()
    class Meta:
        permissions = [
            (PERMISSION_OPEN_DOOR, "Can open any door"),
            (PERMISSION_LOCATION_OVERRIDE, "Can open doors from anywhere"),
        ]


