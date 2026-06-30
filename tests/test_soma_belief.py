"""The belief layer invariants on the real soma's dt.

Two load-bearing claims from the manifesto:
  1. transparency — the descriptor returns the resolved scalar; the
     dissent does not get in the way of computation.
  2. preserved dissent — the overruled voice survives, attributed and
     queryable, so "neither subordinate" is literally true.
"""
from examples.soma_belief import dt_belief, Believed


def test_value_is_transparent():
    """value behaves as the resolved scalar 0.025 for computation."""
    b = dt_belief()
    assert b.value == 0.025
    assert float(b) == 0.025
    assert b == 0.025
    # usable in arithmetic without unwrapping ceremony
    assert float(b) * 4 == 0.1


def test_dissent_is_preserved():
    """The overruled proposal survives, fully attributed."""
    b = dt_belief()
    overruled = [t for t in b.turns if t["epistemic"] == "overruled"]
    assert len(overruled) == 1
    spanda = overruled[0]
    assert spanda["voice"]["name"] == "spanda"
    assert spanda["value"] == 0.01
    assert "divergence" in spanda["rationale"]


def test_resolution_is_attributed():
    """The accepted turn links back to what it answers and who resolved it."""
    b = dt_belief()
    accepted = [t for t in b.turns if t["epistemic"] == "accepted"]
    assert len(accepted) == 1
    win = accepted[0]
    assert win["value"] == 0.025
    assert win["resolved-by"] == "mu2tau"
    assert win["responds-to"]["voice"]["name"] == "spanda"


def test_open_question_travels():
    """The knowingly-traded-away risk stays attached to the value."""
    b = dt_belief()
    assert b.open_question is not None
    assert "artifact" in b.open_question


def test_outcome_fuses_spec_and_receipt():
    """The contested value points at the receipt it produced (cold-reader's ask)."""
    b = dt_belief()
    assert b.outcome is not None
    # the dt=0.025 belief carries the trace-producing receipt's stable facts
    assert b.outcome["density_mechs"]["pas"]["g"] == [0.0001]
