import logging

from django.conf import settings
import graphene
from django.core.handlers.wsgi import WSGIRequest
from graphql import GraphQLError
from icecream import ic

import apitoken.apitoken
from accounts.gql import UsersQuery
from apitoken.gql import ApitokenMutations
from doors.gql import DoorsQuery, DoorsMutations

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


class Query(
    DoorsQuery,
    UsersQuery,
    graphene.ObjectType
):
    if settings.DEBUG:
        from graphene_django.debug import DjangoDebug
        debug = graphene.Field(DjangoDebug, name='_debug')


class Mutation(graphene.ObjectType):
    door = graphene.Field(DoorsMutations)

    @staticmethod
    def resolve_door(self, info):
        return DoorsMutations()
    apitoken = graphene.Field(ApitokenMutations)

    @staticmethod
    def resolve_apitoken(self, info):
        return ApitokenMutations()


class AuthenticationMiddleware(object):
    def resolve(self, next, root, info, **args):
        if info.field_name == 'user':
            auth_header: str = info.context.META.get('HTTP_AUTHORIZATION')
            if auth_header.startswith("Bearer "):
                token = auth_header.removeprefix("Bearer ")
                user = apitoken.apitoken.authenticate(token)
                if isinstance(info.context, WSGIRequest):
                    info.context.user = user
                    # TODO disable csrf
                else:
                    log.error("Context %r is no WSGIRequest", info.context)
        return next(root, info, **args)


schema = graphene.Schema(query=Query, mutation=Mutation)
