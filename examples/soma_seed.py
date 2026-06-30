"""Serialize the passive soma to a *seed* — and germinate it back.

A seed is descripy's durable artifact: not the live object (which is bound
to a NEURON interpreter and cannot be pickled across environments) but a
record from which an equivalent object can be *regenerated*. The thesis:
record the seed, not the archive.

This module is the build-by-use probe for Step 2 (serialize) and Step 3
(germinate + verify). We discovered in soma_passive.py that
``Config.serialize()`` captures the *declared descriptor fields*
(``L, diam, nseg, cm``) but NOT the inserted ``pas`` mechanism, which
lives only in NEURON's ``psection()`` receipt. So a faithful seed must
carry both: the descriptor parameters *and* the biophysics needed to
reconstruct the cell, plus the receipt it is expected to produce.

The seed is bilingual (the human/agent common language): a structured
data record (machine-checkable) carried alongside a natural-language
gloss (human-legible intent).
"""
import hashlib
import json

from examples.soma_passive import build_soma, receipt


# --- the receipt projection -------------------------------------------------
# psection() carries NEURON-internal, run-to-run-volatile keys (e.g.
# 'hoc_internal_name' is a memory address). The seed must compare on the
# *stable* projection only, or the verification hash will never match.

def stable_receipt(psec):
    """Project psection() down to the run-stable facts worth verifying."""
    return {
        "L": psec["morphology"]["L"],
        "diam": list(psec["morphology"]["diam"]),
        "nseg": psec["nseg"],
        "cm": list(psec["cm"]),
        "Ra": psec["Ra"],
        "density_mechs": {
            mech: {p: list(v) for p, v in params.items()}
            for mech, params in psec["density_mechs"].items()
        },
    }


def seed_hash(payload):
    """A content hash over a canonical JSON encoding of the payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


# --- the seed ---------------------------------------------------------------

def make_seed():
    """Serialize the passive soma specimen to a seed record.

    TODO(human): decide the *shape* of the seed dict returned here.

    Constraints discovered by use:
      - soma.serialize() gives the declared params: {'L','diam','nseg','cm'}.
        Get it via ``soma.serialize()``.
      - the pas mechanism (g=0.0001, e=-70.0) is NOT in serialize(); it is
        applied by ``soma.insert_passive(g=..., e=...)`` and shows up only
        in ``stable_receipt(receipt(soma))['density_mechs']``.
      - sim params come from ``sim.serialize()``: {'dt','tstop','v_init'}.
      - the seed must be enough to (1) germinate an equivalent soma+sim in
        soma_germinate.py and (2) be content-hashed for verification.

    The bilingual requirement: include a human-legible natural-language
    gloss alongside the machine record (the "common language" the human
    asked for — natural + programming language together).

    Return a dict. A reasonable spine to fill in:

        {
          "gloss": "<one line of natural language describing this cell>",
          "kind": "Section+Simulation",          # what germinates
          "section": { ... },                     # params + mechanisms
          "simulation": { ... },                  # sim params
          "expect": stable_receipt(receipt(soma)) # the receipt to verify
        }
    """
    sim, soma = build_soma()
    return {
        "gloss": ("A passive single-compartment soma, 10x10 um, leak "
                  "g=0.0001 S/cm2 at e=-70 mV, held 50 ms with no stimulus."),
        "kind": "Section+Simulation",
        "section": {
            "name": soma.name,
            "params": soma.serialize(),          # declared intent: L,diam,nseg,cm
            "mechanisms": {                       # intent applied via insert_passive
                "pas": {"g": 0.0001, "e": -70.0},
            },
        },
        "simulation": sim.serialize(),           # declared intent: dt,tstop,v_init
        "expect": stable_receipt(receipt(soma)), # consequence NEURON computed
    }


if __name__ == "__main__":
    from pprint import pprint

    seed = make_seed()
    print("=== seed ===")
    pprint(seed)
    print("\nseed hash:", seed_hash(seed))
