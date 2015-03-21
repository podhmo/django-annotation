# -*- coding:utf-8 -*-
import unittest


class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from django_annotation import MappingManager, setup
        d = cls.manager = MappingManager(reserved_words=[("label", "*default-label*")])
        setup(cls.manager)

        from django.db import models

        class User(models.Model):
            name = d.CharField(label="this-is-User-name")
            age = d.CharField()

        cls.User = User

    def _getTarget(self):
        from django_annotation import get_mapping
        return get_mapping

    def _callFUT(self, target):
        return self._getTarget()(target, mapping=self.manager)

    def test_it_model(self):
        user = self.User()
        result = self._callFUT(user)
        expected = {'name': {'label': 'this-is-User-name'},
                    'id': {'label': '*default-label*'},
                    'age': {'label': '*default-label*'}}
        self.assertEqual(dict(result), expected)

    def test_it_field(self):
        user = self.User()
        result = self._callFUT(user._meta.get_field("name"))
        expected = {'label': 'this-is-User-name'}
        self.assertEqual(dict(result), expected)

    def test_it_modify_free(self):
        user = self.User()
        result = self._callFUT(user._meta.get_field("name"))
        result.pop("label", None)
        result = self._callFUT(user._meta.get_field("name"))
        expected = {'label': 'this-is-User-name'}
        self.assertEqual(dict(result), expected)
