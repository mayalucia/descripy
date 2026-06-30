"""Nothing can be several things.

`NA` is descripy's explicit absence: a falsy, empty, callable singleton
that is nonetheless `is not None` — so a recorded "not available" survives
the `v is not None` serialization filter and is rendered explicitly (as
`"null"` or dropped) by `serialize_value`, rather than silently vanishing.

This is core, not a util: it sits on the seed path and is part of the
public surface. It leans on `Singleton` from utils (core may use a util;
a util must never need core).
"""
from collections.abc import Mapping

from descripy.utils.singleton import Singleton


class NullType(Singleton, Mapping):
    """..."""
    def __bool__(self):
        """..."""
        return False

    def __str__(self):
        """..."""
        return "<<Not Available>>"

    def __repr__(self):
        """..."""
        return self.__str__()

    def __iter__(self):
        """
        Make null type iterable so that it can be used where an iterable could be."""
        return self

    def __next__(self):
        """A null type contains nothing."""
        raise StopIteration("A null type contains nothing.")

    def __getitem__(self, item):
        """..."""
        raise KeyError("A null type NA cannot contain anythibng.")

    def __len__(self):
        """..."""
        return 0

    def __contains__(self, x):
        """..."""
        return False

    def __call__(self, *args, **kwargs):
        """Finally null type is also callable,
        returning the one and only one instance of itself.
        """
        return NA

    pass


NA = NullType()
