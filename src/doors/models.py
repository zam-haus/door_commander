import uuid

from django.db import models

# Create your models here.
_PERMISSION_OPEN_DOOR = 'open_door'
_PERMISSION_LOCATION_OVERRIDE = 'assume_correct_location'
_APP_NAME = "doors."
PERMISSION_OPEN_DOOR = _APP_NAME+_PERMISSION_OPEN_DOOR
PERMISSION_LOCATION_OVERRIDE = _APP_NAME+_PERMISSION_LOCATION_OVERRIDE

class ActionButton(models.Model):
    class Meta:
        abstract = True
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

class Door(ActionButton):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mqtt_id = models.CharField(max_length=256, unique=True, db_index=True)
    display_name = models.TextField()
    hidden = models.BooleanField(default=False)
    class Meta(ActionButton.Meta):
        permissions = [
            (_PERMISSION_OPEN_DOOR, "Can open any door"),
            (_PERMISSION_LOCATION_OVERRIDE, "Can open doors from anywhere"),
        ]
    def __str__(self):
        return f"Door(display_name={self.display_name},id={self.id})"

class MultiOpen(ActionButton):
    """Elevator or Machine panel, where one open action activates all
    buttons (Doors) that can be opened by the user"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    display_name = models.TextField()
    doors = models.ManyToManyField(Door)
