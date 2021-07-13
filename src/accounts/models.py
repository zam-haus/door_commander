from django.db import models

from django.contrib.auth.models import AbstractUser

from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    first_name = None
    last_name = None

    display_name = models.CharField(_('display name'), max_length=300, blank=True)
    full_name = models.CharField(_('full name'), max_length=300, blank=True)
    password_last_changed = models.DateTimeField(_('password last changed'), default=timezone.now)

    def get_short_name(self):
        return self.display_name

    # For legal matters, not to be displayed publicly; often optional.
    def get_full_name(self):
        return self.full_name

    def set_password(self, raw_password):
        super().set_password(raw_password=raw_password)
        self.password_last_changed = timezone.now()
