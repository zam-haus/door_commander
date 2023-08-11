from uuid import uuid4

from django.contrib import admin

# Register your models here.
from apitoken.models import ApiToken
from doors import door_names_publisher


class ApitokenAdmin(admin.ModelAdmin):
    list_display = (ApiToken.id.field.name, ApiToken.user.field.name,
                    ApiToken.register_mode.field.name, ApiToken.register_mode.field.name,
                    ApiToken.oldest_serial.field.name, ApiToken.newest_serial.field.name)




admin.site.register(ApiToken, ApitokenAdmin)
