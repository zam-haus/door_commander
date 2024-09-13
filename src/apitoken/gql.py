import logging

import graphene
from django.core.handlers.wsgi import WSGIRequest
from uuid import UUID

from icecream import ic

from apitoken import apitoken
from apitoken.models import ApiToken

log = logging.getLogger(__name__)
class Refresh(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    token = graphene.String()

    def mutate(self, info: graphene.ResolveInfo, id):
        try:
            new_token = apitoken.check_permission_and_renew(info.context, id)
            return Refresh(token=new_token)
        except Exception as exc:
            log.error("failed to refresh token", exc_info=True)
            return Refresh(token=None)



class ApitokenMutations(graphene.ObjectType):
    refresh = Refresh.Field()

