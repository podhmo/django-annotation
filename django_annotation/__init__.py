# -*- coding:utf-8 -*-
import logging
from functools import wraps
from singledispatch import singledispatch
from django.db import models
logger = logging.getLogger(__name__)


class MappingManager(object):
    def __init__(self, reserved_word=["doc"]):
        self.mapping = {}
        self.reserved_word = set(reserved_word)
        self.marker = object()

    def add_reserved_word(self, *ws):
        self.reserved_word.update(ws)

    def get(self, k, default=None):
        try:
            return self.mapping[k]
        except KeyError:
            return default

    def __getitem__(self, k):
        return self.mapping[k]

    def __setitem__(self, k, v):
        self.mapping[k] = v

    def register(self, fn):
        logger.debug("register %s.%s", fn.__module__, fn.__name__)
        wrapped = self.wrapper(fn)
        setattr(self, fn.__name__, wrapped)
        return wrapped

    def wrapper(self, fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            options = {}
            for k in self.reserved_word:
                v = kwargs.pop(k, self.marker)
                if v is not self.marker:
                    options[k] = v
            result = fn(*args, **kwargs)
            self.mapping[result] = options
            return result
        return wrapped

default_mapping = MappingManager()


def get_default_mapping():
    global default_mapping
    return default_mapping


def set_default_mapping(mapping):
    global default_mapping
    default_mapping = mapping


@singledispatch
def get_mapping(ob, mapping=None):
    return {}


@get_mapping.register(models.Field)
def mapping__field(field, mapping=None):
    mapping = mapping or get_default_mapping()
    return mapping.get(field) or {}


@get_mapping.register(models.Model)
def mapping__model(ob, mapping=None):
    mapping = mapping or get_default_mapping()
    try:
        return mapping[ob.__class__]
    except KeyError:
        result = {f.name: get_mapping(f, mapping=mapping) for f in ob._meta.fields}
        mapping[ob.__class__] = result
        return result


def setup(mapping, callback=None):
    for k, v in models.__dict__.items():
        if isinstance(v, type) and issubclass(v, models.Field):
            registered = mapping.register(v)
            if callback:
                callback(k, registered)

if __name__ != "__main__":
    import sys
    from django.db import models
    m = sys.modules[__name__]

    def callback(k, registered):
        setattr(m, k, registered)

    setup(default_mapping)
