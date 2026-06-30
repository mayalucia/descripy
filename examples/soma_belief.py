"""The belief layer on the real soma — the dt=0.025 contested turn.

descripy's thesis: record the *provenance of belief* behind a value, not
merely the value. The canonical specimen (manifesto, Part I) is the
=dt=0.01 (spanda) vs 0.025 (mu2tau)= disagreement, resolved to 0.025,
with the dissent *preserved, not deleted*.

This module attaches that belief to the soma seed's ``dt`` and enforces
the load-bearing invariant from the manifesto (Part II, "The belief
layer"):

    "the descriptor returns the resolved scalar transparently — the
     dissent does not get in the way."

So ``believed.value`` must behave as the plain float ``0.025`` for
computation, while ``believed.turns`` / ``believed.open_question`` keep
the conversation queryable.

The primitives, earned by the cold-regeneration test (manifesto):
  - attributed turn: voice, date, value, rationale-in-prose, epistemic
    tag, and a responds-to link to the turn it answers.
  - voice: name + kind, one line.
  - epistemic status: the winner AND the preserved dissent both tagged.
  - the spec-receipt fusion the cold reader demanded: an outcome field —
    did the flagged artifact materialize? (Our lean seed already carries
    this as seed["expect"]; the belief can point at it.)
"""
from descripy.belief import Believed
from examples.soma_seed import make_seed


def dt_belief():
    """Build the dt=0.025 contested turn as attributed voices.

    TODO(human): construct and return a ``Believed`` for the soma's dt.

    The history to record (a genuine contested turn from the NEURON
    bring-up, per the manifesto):
      - spanda proposed dt=0.01 — "smaller step, safer against divergence
        on a stiff active membrane."
      - mu2tau countered dt=0.025 — "matches the NEURON reference we are
        reproducing; fidelity over safety here."
      - resolved to 0.025 (mu2tau resolved it).
      - standing open question: revisit if a subtle artifact appears —
        knowingly traded away.

    Shape each turn however you judge best (the attributed-turn schema is
    *the* MāyāLucIA primitive). A turn needs at least: voice (name+kind),
    date, value, rationale (prose), epistemic tag; the counter-turn also
    a responds-to link. Both the winner and the overruled dissent must
    survive and stay queryable.

    Pass the resolved scalar (0.025) as ``resolved`` so that
    ``dt_belief().value == 0.025`` and ``float(dt_belief()) == 0.025``.
    You may point ``outcome`` at the seed's receipt (the spec-receipt
    fusion the cold reader demanded): ``make_seed()["expect"]``.
    """
    proposal = {
        "voice": {"name": "spanda", "kind": "design consultant (bravli)"},
        "date": "2026-06-15",
        "value": 0.01,
        "rationale": ("Smaller time step is safer against divergence on a "
                      "stiff active membrane."),
        "epistemic": "overruled",
    }
    counter = {
        "voice": {"name": "mu2tau", "kind": "human (principal)"},
        "date": "2026-06-15",
        "value": 0.025,
        "rationale": ("0.025 matches the NEURON reference we are "
                      "reproducing — fidelity over safety here."),
        "epistemic": "accepted",
        "responds-to": proposal,
        "resolved-by": "mu2tau",
    }
    return Believed(
        resolved=0.025,
        turns=[proposal, counter],
        open_question=("Revisit dt if a subtle artifact appears at 0.025 — "
                       "knowingly traded away for reference fidelity."),
        outcome=make_seed()["expect"],
    )


if __name__ == "__main__":
    from pprint import pprint

    believed = dt_belief()
    print("transparent value :", believed.value)
    print("as float          :", float(believed))
    print("equals 0.025      :", believed == 0.025)
    print("\nturns (preserved dissent):")
    pprint(believed.turns)
    print("\nopen question:", believed.open_question)
