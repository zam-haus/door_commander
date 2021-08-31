from django.http import JsonResponse

from door_commander import mqtt
from web_homepage.models import Door


def doors(request):
    return JsonResponse(
        dict(
            doors={
                str(door.id): dict(
                    display_name=door.display_name,
                    mqtt_id=door.mqtt_id,
                ) for door in (Door.objects.all())
            },
            doors_status={
                str(door.id): dict(
                    presence=mqtt.door_commander_mqtt.doors_presence,
                ) for door in (Door.objects.all()) if door.mqtt_id in mqtt.door_commander_mqtt.doors_presence
            },
            __comment="The `doors` dictionary key is the django database/api id, which differs from the mqtt id",
        )
    )
