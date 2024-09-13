import graphene
from django.core.handlers.wsgi import WSGIRequest
from uuid import UUID

from apitoken import apitoken
from apitoken.models import ApiToken


class Refresh(graphene.Mutation):
    class Arguments:
        id = graphene.ID()

    token = graphene.String()

    def mutate(self, info: graphene.ResolveInfo, id):
        new_token = apitoken.check_permission_and_renew(info.context, id)
        return Refresh(token=new_token)



class ApitokenMutations(graphene.ObjectType):
    refresh = Refresh.Field()

