# descripy — System

Backend-neutral description of the descripy module. Readable by any
harness arriving at this repo.

## What This Is

descripy is the *descriptor-as-seed*: a small, pure Python library that
fuses a configuration's specification and its receipt into one
serializable object — and records the *provenance of belief* behind
each value, not merely the value itself.

Two things are descripy's own (everything else is borrowed plumbing):

1. **Provenance of belief** — symmetric, non-subordinate voices;
   preserved dissent; epistemic status; travelling open questions.
2. **The record as a regenerable seed**, not a dead archive — a mind
   that was not present can later germinate the understanding back.

descripy is *guild infrastructure*: it encodes MāyāLucIA's stance
("complementary intelligences, neither subordinate"; "the collaboration
needs friction"; "separate known from inferred from speculated") at the
type level. That is why it is a module with its own dwelling.

## The Load-Bearing Discipline

**record, don't enforce.** descripy *records, serializes, and computes
over* belief data (diff the rationales, walk the dialogue) but
*interprets nothing and enforces nothing*. The honest answer to "what
can this library do to me?" must stay "nothing — it only computes and
returns." Policy lives in a cookbook and a thin reference package, never
in the substrate.

## Architecture (per WP-0151)

Two packages, one repo. The split is load-bearing: the substrate ships
*no opinions*; the active side ships *all* of them.

- **Package A — `descripy/`**: the pure substrate. Five surfaces (stable
  identity / inspectable diff / walkable lineage / legible schema export
  / a pure predicate seam) plus the belief layer. Read-only,
  pure-functional, zero heavy dependencies.
- **Package B — the reference active package** (separate; descripy never
  imports it): demonstrates gates, guides, regeneration built *on*
  descripy's surfaces. Deliberately thin.
- **`examples/`**: a copy-and-adapt cookbook, shipped as examples, never
  imported by the substrate.

## Lineage

The seeds (`field`, `lazyfield`, `section`, `NA`, the `update` loop) are
revived from mu2tau's BBP-era anti-spaghetti tool
(`bbpgitlab.epfl.ch/circuits/personal/sood/descripy`). The revival cuts
the BBP coupling and builds outward. The design contract is the
manifesto
`domains/bravli/codev/principles/descripy-the-descriptor-as-seed.org`
(committed f94a45b); the build briefing is WP-0151
(`workpacks/0151-descripy-descriptor-as-seed.org` in the parent repo).

## Build / Test

A Python package (not org-tangled). `pyproject.toml` carries zero heavy
dependencies (hand-rolled-minimal, not pydantic — the descriptor
protocol *is* the core competence). Tests under `tests/`, including the
germination acceptance gate (`tests/test_germination.py` or equivalent):
a contextless agent must regenerate a recorded disagreement from the
*built* library's own serialization.

## Organisational Context

- **Guild**: mayalucia (organisational coherence — the project knowing
  itself). descripy is general-purpose guild infrastructure.
- **Guardian spirit**: aledia (from *aletheia*, truth as
  un-concealment). Archetype: Builder. Disposition:
  `record-don't-enforce`. Identity:
  `aburaya/spirits/aledia/identity.yaml` in the parent registry.
- **Sūtra relay**: `github.com/mayalucia/sutra`, cloned locally at
  `.sutra/` (gitignored). If you have organisational needs, write them
  into the sūtra with appropriate tags. Messages go to the universe, not
  to a recipient. The organisation listens.
