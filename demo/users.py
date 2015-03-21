# -*- coding:utf-8 -*-
import django
from django.db import models
from django.conf import settings
from django.db import connections
from django.core.management.color import no_style
import django_annotation as d

settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }}
)


def create_table(model):
    connection = connections['default']
    cursor = connection.cursor()
    sql, references = connection.creation.sql_create_model(model, no_style())
    for statement in sql:
        cursor.execute(statement)

    for f in model._meta.many_to_many:
        create_table(f.rel.through)


class Group(models.Model):
    name = d.CharField(max_length=255, verbose_name="Name", doc="名前")

    class Meta:
        app_label = __name__


class User(models.Model):
    group = d.ForeignKey(Group)
    name = d.CharField(max_length=255, verbose_name="Name", doc="名前")

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    from django.conf import settings
    settings.INSTALLED_APPS += (__name__, )
    django.setup()

    user = User()
    print(d.get_mapping(user))  # => {"name": {"doc": "名前"}}

