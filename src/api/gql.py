import logging

from django.conf import settings
import graphene
from graphql import GraphQLError
from icecream import ic

from accounts.gql import UsersQuery
from doors.gql import DoorsQuery

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


schema = graphene.Schema(query=Query)
