from uuid import uuid4

from django.contrib import admin

# Register your models here.
from doors.models import Door
from doors import door_names_publisher


class DoorAdmin(admin.ModelAdmin):
    list_display = (Door.mqtt_id.field.name, Door.display_name.field.name)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields[Door.mqtt_id.field.name].initial = uuid4()
        return form

    def save_model(self, request, obj, form, change):
        super(DoorAdmin, self).save_model(request, obj, form, change)
        door_names_publisher.publish_door_name(obj)


admin.site.register(Door, DoorAdmin)
