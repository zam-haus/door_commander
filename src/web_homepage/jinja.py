from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment
from django.conf import settings


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'debug': settings.DEBUG,
        'oidc_active': settings.OIDC,
    })
    return env
