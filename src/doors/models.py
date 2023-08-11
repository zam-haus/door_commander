import uuid

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
    class Meta:
        ordering = ('order',)
