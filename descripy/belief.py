"""The belief layer — a value carried with the provenance of belief about it.

descripy's thesis: record the *provenance of belief* behind a value, not
merely the value (EPISTEMOLOGY.org Part A, "beliefs about values, not
values"). This module is the mechanism for that — `Believed`, a value that
is transparent for computation while carrying the attributed conversation
that settled it.

Two load-bearing invariants (manifesto, "The belief layer"), both pinned
by the spike's tests on a real NEURON parameter:

  - *transparency* — ``believed.value`` (and ``float``/``==``) behave as
    the resolved scalar, so the dissent never gets in the way of arithmetic.
  - *preserved dissent* — the overruled voice survives in ``turns``, fully
    attributed and queryable, so "neither subordinate" is literally true.

Belief is CORE and exported (EPISTEMOLOGY.org Part C, resolved): the
substrate *offers* the mechanism. The opt-in happens when the programmer
uses it — a value with no turns is not descripy refusing belief, it is a
user who recorded none. What stays OUT of the substrate is the
*elicitation* workflow (prompting for dissent, gating on open questions):
that is policy, and lives in a reference package. Mechanism, not policy.

The attributed-turn schema (earned by the spike, LEARNINGS.org item 3):
a turn is a dict with at least ``voice`` (name + kind), ``date``,
``value``, ``rationale`` (prose), and an ``epistemic`` tag; a counter-turn
also carries ``responds-to`` and ``resolved-by``. It is left as a plain
dict on purpose — the substrate records the schema, it does not impose a
class on the conversation.

`Believed` is the molecule; a single ``epistemic`` tag is its atom — the
thin "standing" end (known/inferred/speculated/borrowed) is to be
extracted from this module by use, not invented ahead of a consumer.
"""


class Believed:
    """A value carried together with the belief about it.

    The resolved scalar is transparent for computation; the provenance is
    queryable but never in the way.
    """
    def __init__(self, resolved, turns, open_question=None, outcome=None):
        self._resolved = resolved
        self.turns = turns
        self.open_question = open_question
        self.outcome = outcome

    @property
    def value(self):
        """The resolved scalar — what computation sees."""
        return self._resolved

    # transparency: behave like the underlying scalar for arithmetic/compare
    def __float__(self):
        return float(self._resolved)

    def __eq__(self, other):
        return self._resolved == (other.value if isinstance(other, Believed) else other)

    def __repr__(self):
        return f"Believed({self._resolved!r}; {len(self.turns)} turns)"
