import inspect

from django.contrib.auth.models import Permission
from django.test import TestCase
from icecream import ic
import django.apps

from . import models


class TestPermissionsDefinition(TestCase):
    def setUp(self) -> None:
        self.app_name = models.__package__
        django_classes = set(django.apps.apps.get_models())
        model_classes = {c for s, c in inspect.getmembers(models, inspect.isclass)}
        classes = django_classes.intersection(model_classes)
        self.permissions = dict()
        for modelclass in classes:
            metaclass = modelclass._meta
            permissions = metaclass.permissions
            self.permissions[modelclass] = permissions

    def tearDown(self) -> None:
        pass

    def test_permissions_on_model(self):
        """our permissions should be defined as codename, not as appname.codename"""
        for modelclass, permissions in self.permissions.items():
            for codename, displayname in permissions:
                self.assertNotIn(".", codename)

    def test_permissions_in_db(self):
        """the permissions should exist in the db"""
        for modelclass, permissions in self.permissions.items():
            for codename, displayname in permissions:
                permission = Permission.objects.get(codename=codename)
                self.assertIsNotNone(permission)

    def test_wrong_permissions_not_in_db(self):
        """the previous permissions should not exist in the db anymore"""
        for modelclass, permissions in self.permissions.items():
            for codename, displayname in permissions:
                with self.assertRaises(django.contrib.auth.models.Permission.DoesNotExist):
                    permission = Permission.objects.get(codename=self.app_name+"."+codename)
                    ic(permission)


    pass
