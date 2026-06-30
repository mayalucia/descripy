"""The parameter — a field promoted to the user-facing configuration surface.

A ``parameter`` is the descriptor specialization that a ``Config`` exposes:
where ``field`` is the substrate primitive and ``section`` is the nested-Struct
specialization, ``parameter`` is the *exposed* one — the knob the analysis
author sets. It carries its own error (``ParamError``) and the config
vocabulary (``of_type``, ``no_such_error``).

It depends on nothing above ``field``: the dependency arrow points only
downward to the descriptor leaf, so ``parameter`` sits at the same tier as
``struct`` (which holds the sibling ``section``), and ``Config`` is built on
top of both. No cycle — unlike the field/Struct pair, ``parameter`` never
references ``Config``.
"""
from descripy.field import field, FieldError


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
