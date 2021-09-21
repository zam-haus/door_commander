import graphene
from graphene_django import DjangoObjectType

from doors import mqtt
from doors.models import Door as DoorModel


class Door(DjangoObjectType):
    class Meta:
        model = DoorModel

    status = graphene.Field('web_homepage.gql.DoorStatus')

    def resolve_status(self, info):
        if self.mqtt_id in mqtt.door_commander_mqtt.doors_presence:
            return (self.mqtt_id, mqtt.door_commander_mqtt.doors_presence[self.mqtt_id])
        else:
            return None


class DoorStatus(graphene.ObjectType):
    door = graphene.Field(Door)
    presence = graphene.Boolean()
    id = graphene.ID()

    def resolve_id(self, info):
        return self[0]

    def resolve_door(self, info):
        mqtt_id = self[0]
        return DoorModel.objects.get(mqtt_id=mqtt_id)

    def resolve_presence(self, info):
        return self[1]


class DoorsQuery(graphene.ObjectType):
    doors = graphene.List(Door)
    doors_status = graphene.List(DoorStatus)

    def resolve_doors(self, info):
        return DoorModel.objects.all()

    def resolve_doors_status(self, info):
        # TODO
        mqtt.door_commander_mqtt.doors_presence[DoorModel.objects.all()[0].mqtt_id] = True
        return mqtt.door_commander_mqtt.doors_presence.items()
