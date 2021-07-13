from django.templatetags.static import static
from django.urls import reverse

from jinja2 import Environment
from door_commander.settings import DEBUG


def environment(**options):
    env = Environment(**options)
    env.globals.update({
        'static': static,
        'url': reverse,
        'debug': DEBUG,
    })
    return env
