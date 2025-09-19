import random
import uuid

from django.db import models

from accounts.models import User
from door_commander import settings
from doors.models import Door


class Card(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    secret_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="cards", help_text="This refers to a user who owns this card", null=True, blank=True)
    disabled = models.BooleanField(default=False, help_text="This card is disabled and cannot be used")

    def __str__(self):
        return str(self.id)


class RegistrationTerminal(models.Model):
    _singleton = models.BooleanField(default=True, editable=False, unique=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(unique=True, help_text="This is the name of the registration terminal")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    door = models.ForeignKey(
        Door, on_delete=models.CASCADE, related_name="registration_terminals",
        help_text="This refers to the door that this registration terminal is assigned to"
    )

    def __str__(self):
        return self.name
