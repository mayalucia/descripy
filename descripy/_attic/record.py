#!/usr/bin/env python3
"""A record of dynamically named key-value pairs, that will act like a Python class instance.
"""
from descripy.struct import NA, field, Struct

def Record(Name, doc="", **kwargs):
    """A record of key-value pairs, as a Python class."""
    def _create_attr(name):
        """Create an attribute..."""
        def record_attribute(self):
            """..."""
            return NA

        record_attribute.__name__ = name
        return field(record_attribute)

    attrs = {key: _create_attr(key) for key in kwargs.keys()}
    RecordType = type(Name, (Struct,), attrs)

    return RecordType(**kwargs)


def struct(name, doc=None, **fields):
    """Create a dynamic Struct."""
    def _create_attr(name, default):
        def class_attr(self):
            return default
        class_attr.__name__ = name
        return field(class_attr)
    attrs = {field: _create_attr(field, value) for field, value in fields.items()}
    return type(name, (Struct,), attrs)
