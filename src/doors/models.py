import uuid

from django.db import models



class Door(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mqtt_id = models.CharField(max_length=256, unique=True, db_index=True)
    display_name = models.TextField()
