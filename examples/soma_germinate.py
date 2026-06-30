"""Germinate a soma from its seed, run it, and verify the round-trip.

This is the acceptance gate in miniature. The lean seed records *intent*
only (params + mechanisms + sim), so germination must *re-derive* the
consequence and prove it matches the seed's recorded ``expect``.

Germination here is *deterministic and templated*: the reference classes
``Section`` / ``Simulation`` (from soma_passive.py) are the rails. The
seed supplies the field values; the template supplies the structure. This
is the concrete form of "templated germination" — an agent (or this
deterministic function) fills a known shape, it does not invent one.

    seed (intent)  --germinate-->  live soma+sim  --run-->  receipt
                                                              |
                              seed["expect"]  ==?  stable_receipt
"""
from examples.soma_passive import Section, Simulation, receipt
from examples.soma_seed import stable_receipt, make_seed, seed_hash


def germinate(seed):
    """Rebuild (sim, soma) from a lean seed, deterministically.

    The reference classes are the template; the seed fills the values.
    """
    secd = seed["section"]
    sim = Simulation(**seed["simulation"])
    soma = Section(secd["name"], **secd["params"])
    for mech, params in secd["mechanisms"].items():
        if mech == "pas":
            soma.insert_passive(g=params["g"], e=params["e"])
        else:
            raise ValueError(f"germination template has no rail for mechanism {mech!r}")
    return sim, soma


def verify(seed):
    """Germinate from the seed, run, and compare receipts.

    Returns (ok, observed, expected). ``ok`` is True iff the re-derived
    consequence matches the recorded one.
    """
    sim, soma = germinate(seed)
    sim.record_voltage(soma, 0.5)
    sim.run()
    observed = stable_receipt(receipt(soma))
    expected = seed["expect"]
    return observed == expected, observed, expected


if __name__ == "__main__":
    from pprint import pprint

    seed = make_seed()
    print("seed hash:", seed_hash(seed))

    ok, observed, expected = verify(seed)
    print("\nround-trip verified:", ok)
    if not ok:
        print("\n--- expected (recorded) ---")
        pprint(expected)
        print("\n--- observed (re-derived) ---")
        pprint(observed)
    else:
        print("the germinated soma reproduces the seed's recorded receipt.")
