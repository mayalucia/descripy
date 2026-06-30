"""The container: a `Struct` of `field`s.

A `Struct` collects the `field` descriptors defined on its class and
manages their values on an instance — loading them from a dict, a YAML
path, or another Struct; serializing them back out. `section` is the
`field` whose value is itself a nested `Struct`.

This module depends on the descriptor (descripy.field); the descriptor
does not depend on it at import time (see field.validate's local import).
`serialize_value` lives here, not in field.py, because it dispatches on
`Struct` — dependency, not topic, fixes its home.
"""
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from lazy import lazy

from descripy.field import (
    field,
    field_of_type,
    lazyfield,
    FieldError,
    MustBeProvidedAtInitialization,
)
from descripy.utils import bounce, slither, load_yaml
from descripy.utils.nothing import NA


def serialize_value(v, na="null"):
    """..."""
    if isinstance(v, Struct):
        return v.serialize(dropna=(na is not None))

    if v is NA:
        return na

    if isinstance(v, Path):
        return v.as_posix()

    if isinstance(v, Enum):
        try:
            return v.description
        except AttributeError:
            return v.value

    return v


class Struct:
    "Of fields."

    @classmethod
    def load_dict_of(cls, fields):
        """..."""
        if fields is None:
            return {}


        try:
            return fields.field_values
        except AttributeError:
            pass

        if isinstance(fields, Mapping):
            return fields

        if isinstance(fields, (str, Path)):
            return load_yaml(fields)

        raise TypeError(f"Cannot initialize {cls.__qualname__} instance "
                        f"from  {type(fields)}")

    def __init__(self, fields=None, skeleton=None,*, strict=False, **input_fields):
        """Initialize by specifying field values as a dict, or keyword arguments,
        or both.

        fields :: An object from which a `Struct` can be loaded,
        ~        1. A Mapping<name -> value> containing field entries
        ~        2. Path to YAML from which this Mapping can loaded
        ~        3. Another `Struct` instance
        skeleton :: The outer `Struct` if this one will be contained in one.

        strict :: Boolean, and if so do not tolerate unknown keywords.
        """
        #LOG.info("Initialize %s with fields in \n%s, and additional inputs \n%s",
                 #self.__class__.__name__, pformat(fields), pformat(input_fields))
        if skeleton:
            #LOG.info("%s is a section inside %s", self.__class__.__name__, skeleton.__class__.__name__)
            self._skeleton = skeleton

        input_fields.update(self.load_dict_of(fields))

        #LOG.info("%s configuration provides fields \n%s",
         #        self.__class__.__name__, pformat(list(input_fields.keys())))

        def _set_field_delegated(f):
            """TODO: test and consider replacing _set_field by this version.
            The used version below needs to know what kind of field it is,
            This version delegates that responsibility to the field itself.
            """
            try:
                value = input_fields.pop(f)
            except KeyError:
                value = None
            setattr(self, f, value)

        def _set_field(f):
            """..."""
            #LOG.debug("Load %s field %s", self.__class__.__name__, f)
            def_field = getattr(self.__class__, f)
            #LOG.debug("\t using definition %s", pformat(def_field._name))
            if def_field.loads_lazily:
                #LOG.debug("\t that loads lazily --- loading will be deferred.")
                return

            try:
                value = input_fields.pop(f)
            except KeyError:
                try:
                    value = input_fields.pop(section.storage_name(f))
                except KeyError:
                    value = def_field(self)

            #LOG.debug("Set %s field %s to value \n%s", self.__class__.__name__, f, pformat(value))
            setattr(self, f, value)

        missing = []
        for f in self.fields:
            try:
                _set_field(f)
            except MustBeProvidedAtInitialization as error:
                missing.append((f, error))

        if missing:
            def name_field(f):
                if isinstance(f, str):
                    return f
                try:
                    return f.__name__
                except AttributeError:
                    pass
                return str(f)

            trace = MustBeProvidedAtInitialization('; '.join([f"{field}: {name_field(error)}"
                                                              for field, error in missing]))
            raise MustBeProvidedAtInitialization(', '.join([f for f,_ in missing])) from trace

        if strict and input_fields:
            raise TypeError(f"Unknown arguments {list(input_fields.keys())}\n"
                            "use strict=False to allow...")

    @classmethod
    def collect_elements(cls, of_type):
        """"..."""
        return [a for a in dir(cls) if isinstance(getattr(cls, a), of_type)]

    @lazy
    def fields(self):
        """..."""
        return  self.collect_elements(of_type=field)

    @property
    def skeleton(self):
        """..."""
        try:
            return self._skeleton
        except AttributeError:
            raise TypeError(f"`Struct` type {self.__class__} is not "
                            "a section in an outer skeleton `Struct`.")
        return None

    def get_element(self, x, of_type):
        """..."""
        terror = of_type.no_such_error(x, instruct=self)

        try:
            xdef = getattr(self.__class__, x)
        except AttributeError as attrocity:
            raise terror from attrocity
        else:
            if not isinstance(xdef, of_type):
                raise terror

        return getattr(self, x)

    def get_element_values(self, of_type):
        """..."""
        elements = self.collect_elements(of_type)
        return {e: self.get_element(e, of_type) for e in elements}

    def get_field(self, attr):
        """..."""
        value = self.get_element(attr, of_type=field)
        if isinstance(value, Struct):
            return value.field_values
        return value

    @lazy
    def field_values(self):
        """Collect `field`s defined in this `Struct` into a dictionary.
        """
        return {f: self.get_field(f) for f in self.fields}


    def serialize(self, fields=None, dropna=True, to_output=None):
        """Serialize the field, values of this `Struct` or a subset.
        """
        data = {f: self.get_field(f) for f in fields} if fields else self.field_values
        to_output = to_output or (lambda obj: obj)
        return to_output({k: v for k, v in data.items() if v is not None})


class SectionError(FieldError):
    """Should when a parameter is missing in a Config.
    """
    pass


class section(field):
    """Section of a configuration.
    """
    @classmethod
    def no_such_error(self, section_name, instruct):
        return SectionError(f"No section named {section_name}"
                            f"in {instruct.__class__.__name__} instance.")

    @classmethod
    def storage_name(cls, attr):
        """Name of an attribute for storage in
        an instance of the object whose class defines it.
        """
        try:
            name = attr.__name__
        except AttributeError:
            assert isinstance(attr, str), type(attr)
            name = attr
        return slither(name)

    def __init__(self, StructType):
        """Initialize a section of a configuration with sections.
        """
        assert issubclass(StructType, Struct)
        self.StructType = StructType
        super().__init__(StructType)

    def validate(self, struct, value):
        """..."""
        if not isinstance(value, Struct):
            return False
        return super().validate(struct, value)

    def __set__(self, skeleton, value):
        """Override `field.__set__.`

        skeleton :: Outer `Struct` instance in which
        this `section` instance is defined.
        """
        value_struct = (value if isinstance(value, self.StructType)
                        else self.StructType(value, skeleton))
        return super().__set__(skeleton, value_struct)

    def __call__(self, skeleton):
        """..."""
        return self.StructType(skeleton=skeleton)
