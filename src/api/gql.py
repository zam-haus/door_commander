import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
import graphene
from graphql import GraphQLError
from icecream import ic

import accounts.models
from door_commander import mqtt
from web_homepage.models import Door as DoorModel

UserModel = get_user_model()

log = logging.getLogger(__name__)


class SecurityMiddleware(object):
    """
    Properly capture errors during query execution and send them to Sentry.
    Then raise the error again and let Graphene handle it.
    """

    def on_error(self, error):
        log.error(ic.format(error))
        expose_details = isinstance(error, GraphQLError) or settings.DEBUG
        raise error if expose_details else Exception("There was an exception. Ask the admin for logs.")

    def resolve(self, next, root, info, **args):
        return next(root, info, **args).catch(self.on_error)


class User(DjangoObjectType):
    class Meta:
        model = UserModel


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


class Query(graphene.ObjectType):
    users = graphene.List(User)
    doors = graphene.List(Door)
    doors_status = graphene.List(DoorStatus)

    if settings.DEBUG:
        from graphene_django.debug import DjangoDebug
        debug = graphene.Field(DjangoDebug, name='_debug')

    def resolve_doors(self, info):
        return DoorModel.objects.all()

    def resolve_doors_status(self, info):
        # TODO
        mqtt.door_commander_mqtt.doors_presence[DoorModel.objects.all()[0].mqtt_id] = True
        return mqtt.door_commander_mqtt.doors_presence.items()

    def resolve_users(self, info):
        user: accounts.models.User = info.context.user
        if user.is_superuser:
            return UserModel.objects.all()
        else:
            raise GraphQLError("Only superusers can access users")


schema = graphene.Schema(query=Query)
