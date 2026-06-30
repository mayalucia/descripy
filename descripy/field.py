"""The descriptor: a `field` of a `Struct`.

A `field` describes one attribute of a structured object — its default
(the decorated method's body), an optional cast, optional lazy loading,
and an optional validation hook. It is a Python descriptor: it lives on
the class and mediates get/set on instances.

This module is the leaf of descripy's dependency graph. It refers to
`Struct` only inside `field.validate`, and does so with a function-local
import, so that `field.py` carries no module-level dependency on the
container — the container (struct.py) depends on the descriptor, never the
other way around.
"""
from pprint import pformat
import logging

#snubbing logging down --- it interferes with the logging of the
#client module using descripy objects. --- example being factology logging
#TODO: There must be a way of using global logging --- figure it out.
LOG = logging.getLogger(__name__)


class MustBeProvidedAtInitialization(TypeError):
    """Use this exception definiing a field that must be initialized.
    """
    pass


class FieldError(AttributeError):
    """Should when a field is missing in a Struct.
    """
    pass


class field:
    """Desciptive Field of a Struct
    """
    @classmethod
    def no_such_error(cls, field_name, instruct):
        return FieldError(f"No field named {field_name} "
                          f"in {instruct.__class__} instance.")

    @classmethod
    def storage_name(cls, from_attr_name):
        """Name of an attribute for storage in
        an instance of the object whose class defines it.
        """
        return f"_{from_attr_name}"

    def __init__(self, attribute=None, cast=None, to_load_lazily=False):
        """Define a class attribute as a `field`."""
        if attribute:
            self._def = attribute
            self.__doc__  = self._def.__doc__
            self._name = self.storage_name(self._def)
        self._cast = lambda value: cast(value) if cast else value
        self._lazy = to_load_lazily

    def __set_name__(self, StructType, attr):
        """Can be used in Python3.9 to initialize properties of a descriptor.
        May not be useful when we want to set other attributes,
        as we have for `field`.
        We can define a customized type constructor (metaclass) for  such cases.
        """
        self._name = self.storage_name(attr)

    @property
    def loads_lazily(self):
        """..."""
        return self._lazy

    def default_value(self, config):
        """..."""
        return self._def(config)

    def __get__(self, struct, StructType):
        """Assuming that `struct` is an instance of `StructType`.
        """
        if not struct:#must have been called on class `StructType` itself, not instance
            assert StructType
            return self

        try:
            return getattr(struct, self._name)
        except AttributeError:
            if self._lazy:
                value = self._def(struct)
                self.__set__(struct, value)
                return value
        try:
            return self._def(struct)
        except MustBeProvidedAtInitialization:
            pass
        raise ValueError(f"Neither set nor defaulted {self._def.__name__}.")

    def validation(self, method):
        """..."""
        self._validation = method
        return self

    def validate(self, struct, value):
        """..."""
        from descripy.struct import Struct
        if not isinstance(struct, Struct):
            return False

        cvalue = self._cast(value)

        try:
            valid = self._validation
        except AttributeError:
            return cvalue

        return valid(struct, cvalue)
        #return cvalue if valid(struct, cvalue) else NA

    def __set__delegated(self, struct, value):
        """__set__ below assumes that a non-None value is passed.
        In this version we assume that `None` means the value was
        not available at initialization of the struct, and that it's
        value may have have been defaulted in the class definition of
        the field.
        """
        if value is None:
            value = self._def(struct)
        valid = self.validate(struct, value)
        assert valid is not None,\
            f"INVALID value {valid} for field {self._def.__name__}"

        setattr(struct, self._name, valid)
        return self

    def __set__(self, struct, value):
        """Set value of this field in a struct.
        """
        LOG.debug("Validate and set %s field %s from value \n%s", struct, self._name, pformat(value))
        setattr(struct, self._name, self.validate(struct, value))
        return self

    def __call__(self, struct):
        """Call on the struct's definition."""
        return self._def(struct)


def field_of_type(T):
    """..."""
    def _field(def_):
        """..."""
        return field(def_, T)
    return _field


def lazyfield(attribute, of_type=None):
    """..."""
    if not of_type:
        return field(attribute, to_load_lazily=True)
    def _field(def_):
        return field(attribute, T, to_load_lazily=True)
    return _field
