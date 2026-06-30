"""Describe and configure analyses.

The public surface is exactly what is *known* (EPISTEMOLOGY.org Part C):
the describe primitives, the substrate primitives, serialization, and the
belief layer. `Believed` is offered as mechanism — present in the surface,
used at the programmer's discretion (the opt-in is its use, not import).
Speculated code (Record, struct(), Entity/Component) lives in `_attic/`
and is deliberately not exported.
"""
from .nothing import NA
from .field import field, lazyfield, field_of_type, FieldError, MustBeProvidedAtInitialization
from .struct import Struct, section, serialize_value
from .config import Config, parameter, ParamError
from .belief import Believed
