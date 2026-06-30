"""Characterization tests for the *inferred* substrate.

These pin the ACTUAL behavior of field / lazyfield / Struct /
serialize_value as it is today — quirks included — so that the coming
restructure (Part C of EPISTEMOLOGY.org) fails loudly if it changes a
contract by accident. Per the epistemic map: these rows are *inferred*
(load-bearing but untested); a green characterization suite promotes them
to *known*.

The discipline is descriptive, not aspirational: where the code does
something surprising, we assert the surprise. A deliberate change to the
contract should show up here as a deliberate edit, never as a silent
regression.
"""
from enum import Enum
from pathlib import Path

from descripy.struct import (
    field,
    lazyfield,
    Struct,
    serialize_value,
    MustBeProvidedAtInitialization,
    FieldError,
)
from descripy.nothing import NA


# --------------------------------------------------------------------------
# field — the descriptor: default, set, validation, class-access
# --------------------------------------------------------------------------

class Plain(Struct):
    @field
    def x(self):
        "doc for x"
        return 41


def test_field_default_comes_from_method_body():
    """An unset field defaults to the value its method body returns."""
    assert Plain().x == 41


def test_field_set_overrides_default():
    assert Plain(x=7).x == 7


def test_field_doc_is_carried_from_the_method():
    assert Plain.x.__doc__ == "doc for x"


def test_class_access_returns_the_descriptor_itself():
    """Accessing the field on the class (not an instance) yields the field.

    struct.py:75 `if not struct:` — class access passes struct=None.
    """
    assert isinstance(Plain.x, field)


class Validated(Struct):
    @field
    def y(self):
        return 10

    @y.validation
    def y(self, value):
        return value * 2


def test_validation_runs_on_set():
    assert Validated(y=5).y == 10  # 5 * 2


def test_validation_also_shapes_the_default_at_init():
    """The init path validates the default too, so the stored value is 20.

    `_set_field` calls __set__ -> validate even when the value came from
    the field's own default. So a freshly-built Validated reads back 20,
    not the bare default 10.
    """
    assert Validated().y == 20


class TrustingValidation(Struct):
    @field
    def z(self):
        return 0

    @z.validation
    def z(self, value):
        return None  # a validator that rejects everything by returning None


def test_set_trusts_validate_blindly_even_when_it_returns_none():
    """__set__ stores whatever validate returns — including None.

    struct.py:132 has no guard; the defensive `__set__delegated`
    (with `assert valid is not None`) is dead code. We pin the live,
    unguarded behavior.
    """
    obj = TrustingValidation(z=99)
    assert obj._z is None


def test_required_field_invariant_is_enforced_by_the_constructor():
    """MustBeProvidedAtInitialization is a *constructor* guarantee.

    A required field (its default raises MustBeProvidedAtInitialization) is
    enforced at __init__: you cannot obtain an instance that lacks it. So
    the question of reading such a field off a live instance never arises —
    and __get__'s line-90 ValueError fallthrough is unreachable by
    construction (a defensive dead branch, like __set__delegated).
    """
    class Req(Struct):
        @field
        def required(self):
            raise MustBeProvidedAtInitialization()

    # no instance exists without the field; the error names the field
    try:
        Req()
        raised = None
    except MustBeProvidedAtInitialization as error:
        raised = str(error)
    assert raised == "required"

    # once provided at init, the field reads back normally
    assert Req(required=5).required == 5


# --------------------------------------------------------------------------
# lazyfield — memoization contract
# --------------------------------------------------------------------------

def test_lazyfield_defers_then_memoizes():
    """A lazyfield is not computed at init, computed once on first read,
    then cached (the method body runs exactly once)."""
    calls = []

    class Lazy(Struct):
        @lazyfield
        def w(self):
            calls.append(1)
            return 7

    obj = Lazy()
    assert calls == []          # not computed at init
    assert obj.w == 7
    assert obj.w == 7
    assert calls == [1]         # computed exactly once


# --------------------------------------------------------------------------
# Struct — collect_elements, field_values, serialize, required-fields
# --------------------------------------------------------------------------

def test_collect_elements_finds_fields_by_type():
    assert sorted(Validated().fields) == ["y"]


def test_field_values_collects_every_field():
    class Two(Struct):
        @field
        def a(self):
            return 1

        @field
        def b(self):
            return 2

    assert Two().field_values == {"a": 1, "b": 2}


def test_serialize_drops_none_but_keeps_NA():
    """`serialize(dropna=True)` filters `v is not None` — so Python None is
    dropped, but NA (which `is not None`) survives.

    The `dropna` name is misleading: NA-dropping is `serialize_value`'s
    job (na=None), not this filter's. Pinned as-is.
    """
    class Mixed(Struct):
        @field
        def a(self):
            return 1

        @field
        def b(self):
            return NA

        @field
        def c(self):
            return None

    out = Mixed().serialize()
    assert out["a"] == 1
    assert out["b"] is NA       # NA is kept
    assert "c" not in out       # None is dropped


def test_unknown_attr_raises_FieldError():
    with __import__("pytest").raises(FieldError):
        Validated().get_field("nope")


# --------------------------------------------------------------------------
# serialize_value — the four cases + passthrough
# --------------------------------------------------------------------------

def test_serialize_value_NA_becomes_the_na_token():
    assert serialize_value(NA) == "null"
    assert serialize_value(NA, na=None) is None


def test_serialize_value_path_becomes_posix_string():
    assert serialize_value(Path("/a/b")) == "/a/b"


def test_serialize_value_enum_uses_value_when_no_description():
    class Color(Enum):
        R = "red"

    assert serialize_value(Color.R) == "red"


def test_serialize_value_struct_recurses():
    assert serialize_value(Plain()) == {"x": 41}


def test_serialize_value_passes_scalars_through():
    assert serialize_value(123) == 123
    assert serialize_value("hi") == "hi"
