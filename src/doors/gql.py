import graphene
from django.core.handlers.wsgi import WSGIRequest
from graphene_django import DjangoObjectType
from graphql import GraphQLError

import doors.open
from doors import mqtt
from doors.models import Door as DoorModel


class Door(DjangoObjectType):
    class Meta:
        model = DoorModel

    status = graphene.Field('doors.gql.DoorStatus')

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



class OpenDoorMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    ok = graphene.Boolean()

    def mutate(self, info: graphene.ResolveInfo, id):
        # TODO https://github.com/graphql-python/graphene-django/issues/345
        if isinstance(info.context, WSGIRequest):
            success = doors.open.check_permission_and_open(id, info.context)
            if not success:
                raise GraphQLError("Not authorized.")
        return OpenDoorMutation(ok=True)





class DoorsMutations(graphene.ObjectType):
    open_door = OpenDoorMutation.Field()
