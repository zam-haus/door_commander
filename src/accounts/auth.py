import json
from logging import getLogger

from django.contrib.auth.models import Permission
from django.db import transaction, IntegrityError
from django.http import HttpRequest
from django.template.defaultfilters import urlencode
from django.template.defaulttags import url
from mozilla_django_oidc.auth import OIDCAuthenticationBackend
from icecream import ic

from accounts.models import User, UserDirectory, UserConnection
from django.conf import settings
from pymaybe import maybe

log = getLogger(__name__)


class CustomOidcAuthenticationBackend(OIDCAuthenticationBackend):
    OIDC_USER_DIRECTORY_UUID = "3a01ea23-4a7f-4c64-adce-02411cd0a480"

    def filter_users_by_claims(self, claims):
        try:
            # return super().filter_users_by_claims(claims)
            log.debug(ic.format(claims))
            # return a user with the key from the token an the correct directory.
            # the two constraints refer to a single directory,
            #   see https://docs.djangoproject.com/en/3.2/topics/db/queries/#spanning-multi-valued-relationships
            users = User.objects.filter(
                connections__directory__id=CustomOidcAuthenticationBackend.OIDC_USER_DIRECTORY_UUID,
                connections__directory_key=self.get_directory_key(claims), )
            log.debug(ic.format(list(users)))
            return users
        except:
            log.info("User not found, creating entry.")
            return self.UserModel.objects.none()

    def get_or_create_directory(self):
        try:
            dir, created = UserDirectory.objects.get_or_create(
                id=CustomOidcAuthenticationBackend.OIDC_USER_DIRECTORY_UUID,
                defaults=dict(
                    name="oidc",
                    description=f"""OpenID Connect Directory at {settings.OIDC_OP_AUTHORIZATION_ENDPOINT}"""
                ))
        except IntegrityError:
            log.error(
                "Could not create a user directory with name 'oidc'. Please rename already existing user directories")
            raise
        else:
            if created:
                log.info("Created user directory %r", dir.name)
            return dir

    def create_user(self, claims):
        dir = self.get_or_create_directory()
        with transaction.atomic():
            user = User()
            user.email = claims.get("email")
            if claims.get("email_verified") is False:
                user.email = None
            user.full_name = claims.get("name")
            user.display_name = claims.get("preferred_username")
            user.set_unusable_password()
            # TODO we might need a way to choose another username if the one here is already taken.
            #  currently, this will raise an exception when a user is redefined due to a unique constraint.
            user.username = claims.get("preferred_username")
            user.save()

            connection = UserConnection()
            connection.user = user
            connection.directory = dir
            connection.directory_key = self.get_directory_key(claims)
            connection.latest_directory_data = claims

            connection.save()
            self.update_permissions(claims, user)
        return user

        # super(CustomOidcAuthenticationBackend, self).create_user(claims)

    def get_directory_key(self, claims):
        return claims["ldap_id"]

    def update_user(self, user, claims):
        # super(CustomOidcAuthenticationBackend, self).update_user(user, claims)
        connection = UserConnection.objects \
            .filter(
            user=user,
            directory__id=CustomOidcAuthenticationBackend.OIDC_USER_DIRECTORY_UUID,
            directory_key=self.get_directory_key(claims),
        ).get()
        connection.latest_directory_data = claims
        connection.save()

        self.update_permissions(claims, user)
        return user

    def update_permissions(self, claims, user):
        # TODO this dead code is still here because I'd like to specify django superuser/permission status via request to an OPA policy
        if False:
            claim_resource_access = maybe(claims) \
                ["resource_access"]["sesam.zam.haus"] \
                ["roles"].__contains__("MayOpenFrontDoor")
            #ic([(p.name, p.codename) for p in Permission.objects.all()])
            permission = Permission.objects.get(codename="open_door")
            if claim_resource_access.or_else(False):
                user.user_permissions.add(permission)
            else:
                user.user_permissions.remove(permission)
            user.save()
        return


def provider_logout(request: HttpRequest):
    keycloak_logout_url = settings.OIDC_OP_LOGOUT_URL
    redirect_url = request.build_absolute_uri(settings.LOGOUT_REDIRECT_URL)
    # required OIDC_STORE_ID_TOKEN=True
    id_token_hint = request.session['oidc_id_token']
    return_url = keycloak_logout_url.format(redirect_url=urlencode(redirect_url),id_token=urlencode(id_token_hint))
    return return_url
