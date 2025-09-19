from uuid import uuid4

from django.contrib import admin
from django.forms import ModelForm
from django.forms.widgets import TextInput

from doors.models import Door, MultiOpen,RemoteClient
from door_commander.random_passwords import generate_password
from doors import door_names_publisher
from doors import mqtt_dynsec


class DoorForm(ModelForm):
    class Meta:
        model = Door
        fields = "__all__"
        widgets = {
            "text_color": TextInput(attrs={"type": "color"}),
            "button_color": TextInput(attrs={"type": "color"}),
        }
class RemoteClientForm(ModelForm):
    class Meta:
        model = RemoteClient
        fields = "__all__"


@admin.register(Door)
class DoorAdmin(admin.ModelAdmin):
    form = DoorForm
    list_display = (Door.mqtt_id.field.name, Door.display_name.field.name)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields[Door.mqtt_id.field.name].initial = uuid4()
        return form

    def save_model(self, request, obj, form, change):
        super(DoorAdmin, self).save_model(request, obj, form, change)
        door_names_publisher.publish_door_name(obj)

@admin.register(RemoteClient)
class RemoteClientAdmin(admin.ModelAdmin):
    form = RemoteClientForm
    list_display = (RemoteClient.username.field.name,)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields[RemoteClient.username.field.name].initial = uuid4()
        form.base_fields[RemoteClient.token.field.name].initial = generate_password()
        return form

    def save_model(self, request, obj, form, change):
        super(RemoteClientAdmin, self).save_model(request, obj, form, change)
        mqtt_dynsec.update_mqtt_client(obj)

    def delete_model(self, request, obj):
        super(RemoteClientAdmin, self).delete_model(request, obj)
        mqtt_dynsec.cleanup_all_clients_and_roles()

admin.site.register(MultiOpen)
