import uuid

import encrypted_fields
from django.db import models

# Create your models here.
_PERMISSION_OPEN_DOOR = 'open_door'
_PERMISSION_LOCATION_OVERRIDE = 'assume_correct_location'
_APP_NAME = "doors."
PERMISSION_OPEN_DOOR = _APP_NAME+_PERMISSION_OPEN_DOOR
PERMISSION_LOCATION_OVERRIDE = _APP_NAME+_PERMISSION_LOCATION_OVERRIDE


class Door(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mqtt_id = models.CharField(max_length=256, unique=True, db_index=True)
    display_name = models.TextField()
    class Meta:
        permissions = [
            (_PERMISSION_OPEN_DOOR, "Can open any door"),
            (_PERMISSION_LOCATION_OVERRIDE, "Can open doors from anywhere"),
        ]
    def __str__(self):
        return f"Door(display_name={self.display_name},id={self.id})"

class MultiOpen(models.Model):
    """Elevator or Machine panel, where one open action activates all
    buttons (Doors) that can be opened by the user"""


    class Meta:
        ordering = ('order',)
    order = models.IntegerField(help_text="Order of appearance for door buttons. Lower is higher up.", default=42)
    text_color = models.CharField(
        max_length=7,
        default="#ffffff",
        null=True,
        help_text="HTML hex color code for text on button")
    button_color = models.CharField(
        max_length=7,
        default="#60b177",
        help_text="HTML hex color code for button")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.TextField()
    doors = models.ManyToManyField(Door)

    def __str__(self):
        return f"MultiOpen({self.mqtt_id=!r}, {self.display_name=!r})"

class RemoteClient(models.Model):
    "An MQTT and OPA client running on an RPI"
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=256, unique=True, db_index=True)

    # The OPA bundle server bearer token or the MQTT password
    token = encrypted_fields.EncryptedCharField(max_length=256)

    doors = models.ManyToManyField(Door, related_name='remote_clients', blank=True)
    "The list of doors that this client is allowed to update on MQTT"