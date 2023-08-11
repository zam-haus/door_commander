import uuid

from django.db import models
from django.db.models import Q, F

from accounts.models import User


class ApiToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    oldest_serial = models.PositiveBigIntegerField(default=0)
    newest_serial = models.PositiveBigIntegerField(default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="api_tokens",
                             help_text="This is the user the api token authorizes as.")
    register_mode = models.BooleanField(
        default=False,
        help_text="Enabling this checkbox will allow any client to refresh this token once."
                  "This is a security risk, only use this for setting up new devices and check the functionality of your token immediately."
                  "It will also automatically be disabled upon any successful authorization.")
    sync_mode = models.BooleanField(
        default=False,
        help_text="Enabling this checkbox will allow a client with an expired token to refresh this token once. "
                  "This is a security risk, only use this after loss of synchronization with an end device (which may indicate api token theft)."
                  "It will also automatically be disabled upon any successful authorization.")

    class Meta:
        constraints = [
            models.CheckConstraint(check=Q(oldest_serial__lte=F('newest_serial')), name="serial_range_constraint")
        ]
