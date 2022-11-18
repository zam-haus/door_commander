import json

from django.core import serializers


def serialize_model(model):
    return json.loads(serializers.serialize('json', [model, ]))[0]
