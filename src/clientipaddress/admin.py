from uuid import uuid4

from django.contrib import admin

# Register your models here.
from clientipaddress.models import WifiLocator


class WifiLocatorAdmin(admin.ModelAdmin):
    list_display = (WifiLocator.mqtt_id.field.name, WifiLocator.display_name.field.name)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields[WifiLocator.mqtt_id.field.name].initial = uuid4()
        return form

admin.site.register(WifiLocator, WifiLocatorAdmin)
