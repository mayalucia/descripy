


# #+title: Entity

# A ~brain-circuit~ is an ~Entity~,

# #+name: init-module
# #+header: :exports both :eval no-export
# #+header: :padline yes :comments both

# [[file:entity.org::init-module][init-module]]
"""Define a configurable Entity.
"""
from descripy.config import (Path, Enum, lazy,
                             NA,
                             serialize_value, field, lazyfield, field_of_type, parameter,
                             Struct, Config, section as config_section,
                             FieldError, ParamError, MustBeProvidedAtInitialization)


class Component(Struct):
    """A component can be placed inside an Entity."""

    @field
    def config(self):
        """A configuration in the form of a dict that sets self parameters."""
        raise MustBeProvidedAtInitialization(Component.config)


class Entity(Struct):
    """Data and behavior of a simulation entity."""
    @classmethod
    @property
    def ID(cls):
        """A label to use in data-frame columns for rows about an Entity."""
        return f"{cls.__name__.lower()}_id"

    @field
    def id(self):
        """Integer id of this Entity."""
        return id(self)

    @field
    def config(self):
        """A configuration in the form of a dict that sets self parameters."""
        raise MustBeProvidedAtInitialization(Entity.config)

    @field
    def methods(self):
        """A handle to an object that implements the functionality
        mentioned in this Entity's config.
        """
        return NA

    @field
    def components(self):
        """A sequence of components of this Entity."""
        return NA
# init-module ends here
