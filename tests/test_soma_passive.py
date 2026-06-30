"""Green-spike test: descriptor -> NEURON -> run -> result.

Asserts the passive single-compartment soma builds, that the descriptor
values land in NEURON's live object (visible in the psection() receipt),
and that a run produces a stable resting trace.

NEURON is bound to one interpreter on this machine; run with::

    PYTHONPATH=. /Users/vishalsoodmuchu/.vmgr_repo/py311/bin/python -m pytest tests/
"""
import pytest

pytest.importorskip("neuron")

from examples.soma_passive import build_soma, receipt


def test_descriptor_values_resolve():
    """The @parameter defaults and overrides resolve to plain scalars."""
    sim, soma = build_soma()
    assert soma.L == 10.0
    assert soma.diam == 10.0
    assert soma.nseg == 1
    assert sim.dt == 0.025
    assert sim.v_init == -70.0
    assert sim.tstop == 50.0


def test_receipt_reflects_descriptor():
    """The descriptor values land in NEURON's live object (the receipt)."""
    _, soma = build_soma()
    psec = receipt(soma)
    assert psec["morphology"]["L"] == 10.0
    assert psec["morphology"]["diam"] == [10.0]
    assert psec["density_mechs"]["pas"]["g"] == [0.0001]
    assert psec["density_mechs"]["pas"]["e"] == [-70.0]


def test_run_is_green_and_resting():
    """A passive cell with no stimulus rests at its leak reversal."""
    sim, soma = build_soma()
    sim.record_voltage(soma, 0.5)
    result = sim.run()
    trace = result["recordings"][("soma", 0.5)]
    assert len(trace) == 2001  # tstop / dt + 1
    assert trace[0] == pytest.approx(-70.0)
    assert trace[-1] == pytest.approx(-70.0)
