"""Acceptance gate: lean seed -> germinate -> run -> receipt matches.

The seed records intent only; germination must re-derive the consequence
(including NEURON defaults like Ra that were never declared) and reproduce
the recorded receipt exactly.
"""
import pytest

pytest.importorskip("neuron")

from examples.soma_seed import make_seed, seed_hash
from examples.soma_germinate import germinate, verify


def test_seed_is_lean():
    """The seed records intent, not the full consequence."""
    seed = make_seed()
    # intent the user chose
    assert seed["section"]["params"]["L"] == 10.0
    assert seed["section"]["mechanisms"]["pas"]["g"] == 0.0001
    assert seed["simulation"]["dt"] == 0.025
    # Ra is a NEURON default — it belongs to the consequence, not the intent
    assert "Ra" not in seed["section"]["params"]
    assert seed["expect"]["Ra"] == 35.4


def test_seed_hash_is_stable():
    """The same intent yields the same content hash across builds."""
    assert seed_hash(make_seed()) == seed_hash(make_seed())


def test_germination_round_trip():
    """The germinated soma reproduces the seed's recorded receipt."""
    seed = make_seed()
    ok, observed, expected = verify(seed)
    assert ok, f"receipt mismatch:\nobserved={observed}\nexpected={expected}"


def test_germinated_object_is_live():
    """Germination yields a runnable soma, not just data."""
    seed = make_seed()
    sim, soma = germinate(seed)
    assert soma.L == 10.0
    assert soma.hoc.psection()["density_mechs"]["pas"]["g"] == [0.0001]
