"""Configurations for computational analyses.
"""
from enum import Enum
from pathlib import Path
from lazy import lazy

from descripy.struct import (serialize_value, field, lazyfield, field_of_type,
                             Struct, section, FieldError,
                             MustBeProvidedAtInitialization)
from descripy.record import Record
from descripy.nothing import NA


class ParamError(FieldError):
    """Should when a parameter is missing in a Config.
    """
    pass


class parameter(field):
    """A parameter is a field to be exposed in the configuration
    of an analyses.
    """
    def __init__(self, maybe_field, *args, **kwargs):
        """Initialize from a field.
        Intended use is as a second decorator on top of `field`.
        This will free `parameter` to be used with a `lazyfield`,
        hence defining a `lazyparameter`.
        We will also extend the implementation of `Config` to
        be able to define class fields as parameters at initialization,
        instead of only at class definition.
        """
        definition = maybe_field._def if isinstance(maybe_field, field) else maybe_field
        super().__init__(attribute=definition, *args, **kwargs)

    @classmethod
    def of_type(cls, T):
        """Parameter of specified type.
        """
        def typed_parameter(method):
            """..."""
            return cls(method, cast=T)
        return typed_parameter

    @classmethod
    def no_such_error(cls, param_name, instruct):
        """..."""
        class_name = instruct.__class__.__name__
        return ParamError(f"No parameter named {param_name} in {class_name} instance.")


class Config(Struct):
    """Configuration for computational analyses.
    """
    @field
    def label(self):
        """..."""
        return self.__class__.__name__

    @lazy
    def parameters(self):
        """Parameters defined in Configuration subclass `cls`.
        """
        return self.collect_elements(of_type=parameter)

    @lazy
    def sections(self):
        """Sections defined in Configuration subclass `cls`.
        """
        return self.collect_elements(of_type=section)

    def get_parameter(self, p):
        """..."""
        value = self.get_element(p, of_type=parameter)
        assert not isinstance(value, Struct),(
            "A nested `Config` / `Struct` instance must not be a parameter,"
            " but a section")
        return value

    @lazy
    def parameter_values(self):
        """Collect parameters of this configuration into a dictionary.
        """
        return {p: self.get_parameter(p) for p in self.parameters}

    def get_section(self, s, element_types=None):
        """..."""
        value = self.get_element(s, of_type=section)
        assert isinstance(value, Struct),(
            "A section must be a `Struct` / `Config` instance.")

        element_types = element_types or [field]
        return {k: v for et in element_types
                for k, v in value.get_element_values(of_type=et).items()}


    def serialize_doesnt_work_for_nested(self, to_output=None):
        """Serialize sections and parameters to an output format
        """
        parameter_values = self.parameter_values.items()
        data = {p: serialize_value(v) for p, v in parameter_values}

        element_types = [parameter, section]
        section_values = {s: self.get_section(s, element_types)
                          for s in self.sections}.items()
        data.update({s: serialize_value(v) for s, v in section_values})
        if not to_output:
            return data
        return to_output(data)


    def _serialize_sections(self, keep_na):
        """..."""
        sections = {s: self.get_element(s, of_type=section) for s in self.sections}
        return {section.storage_name(n): sxn.serialize(keep_na)
                for n, sxn in sections.items()}

    def serialize(self, dropna=True, to_output=None):
        """..."""
        data = {p: serialize_value(v, na=("null" if not dropna else None))
                for p, v in self.parameter_values.items()}
        data.update(self._serialize_sections(dropna))

        data = {k: v for k, v in data.items() if v is not None}

        if not to_output:
            return data
        return to_output(data)

    @parameter
    def status(self):
        """Status of the task that this class configures.
        Has it been run? Was the result successful?
        The default of NA / None indicates that the configuraiton has not been
        used for any task yet.
        If the configuration has been used, then a copy can be attached to the
        result of the task. In such a case the value of this parameter may
        depend on the particular `Config` subclass definition.
        Furthermore, output sections may be added to the config, or set to
        non-NA values that describe the result of running the task.
        """
        return NA

    @parameter
    def output(self):
        """Location where the output of running this configuration should go.
        """
        return NA

    def update(self, status=None, output=None):
        """..."""
        fields = self.serialize()
        if status: fields["status"] = status
        if output: fields["output"] = output
        return self.__class__(fields)
