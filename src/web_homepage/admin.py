from django.contrib import admin
from uuid import uuid4

from web_homepage.models import Door


class DoorAdmin(admin.ModelAdmin):
    list_display = (Door.mqtt_id.field.name, Door.display_name.field.name)
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields[Door.mqtt_id.field.name].initial = uuid4()
        return form


admin.site.register(Door, DoorAdmin)
