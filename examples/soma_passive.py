"""The single-compartment passive soma — descripy's first crucible.

Distilled from the teaching workbook
``~/work/bbp/work/bravlibpy/learn/cells/simulation.org`` (the Oren Amsalem
single-compartment specimen at its line 775), reduced to *passive-only* so
that it runs against NEURON built-ins alone (no compiled NMODL).

What this exercises, end to end:

    recipe (pure science: @parameter)  --germinate-->  live Model (self.hoc)
        ->  run the simulation         ->  a result (psection() receipt)

This is the loop descripy's "descriptor-as-seed" thesis is about, now
carved at the honest seam: a ``ModelRecipe`` records *intent* only (the
chosen parameters, no engine), and ``recipe.germinate()`` re-derives the
live NEURON object — the *consequence*. The germinate override is the
science→engine seam: where a recorded belief becomes a running model.

Run (NEURON is bound to the py311 interpreter on this machine)::

    /Users/vishalsoodmuchu/.vmgr_repo/py311/bin/python examples/soma_passive.py
"""
from descripy.model import ModelRecipe, Model
from descripy.param import parameter
from descripy.struct import lazyfield
from descripy.nothing import NA

from neuron import h


class SectionModel(Model):
    """A live NEURON section: the germinated body of a ``SectionRecipe``.

    Holds ``self.hoc`` (the engine object) and the morphology pushed into
    it. Reads of ``L`` / ``diam`` / ``nseg`` / ``cm`` go through to the
    live object, so the model reports what NEURON actually holds.
    """
    def _push_morphology(self, recipe):
        """Push the recipe's morphology parameters into the live hoc."""
        self.hoc.nseg = recipe.nseg
        self.hoc.L = recipe.L
        self.hoc.diam = recipe.diam
        self.hoc.cm = recipe.cm
        return self

    def insert_passive(self):
        """Insert the leak the recipe records — a no-op when it records none.

        The recipe is the single source of truth for the leak: ``passive``
        is ``NA`` (falsy) for "no leak", else ``{'g':.., 'e':..}``. Folding
        the condition in here keeps ``germinate`` a clean chain.
        """
        leak = self.recipe.passive
        if not leak:
            return self
        self.hoc.insert("pas")
        for seg in self.hoc:
            seg.pas.g = leak["g"]
            seg.pas.e = leak["e"]
        return self

    def segment(self, position):
        """Access a segment at a relative position (0 < value < 1)."""
        return self.hoc(position)

    def __call__(self, position):
        """Access a segment in this section (e.g. ``soma(0.5)``)."""
        return self.hoc(position)

    @property
    def name(self):
        return self.recipe.name

    @property
    def L(self):
        return self.hoc.L

    @property
    def diam(self):
        return self.hoc.diam

    @property
    def nseg(self):
        return self.hoc.nseg

    @property
    def cm(self):
        return self.hoc.cm


class SectionRecipe(ModelRecipe):
    """The pure science of a neuronal section: morphology + (optional) leak.

    No NEURON here — constructing a recipe records intent only. Each
    ``@parameter`` carries a default (the method body). ``germinate()``
    builds the live ``SectionModel``.
    """
    @parameter
    def name(self):
        """Name of this section (e.g. 'soma')."""
        return "section"

    @parameter
    def nseg(self):
        """Number of segments to model in this section."""
        return 1

    @parameter
    def L(self):
        """Length of section (um)."""
        return 20.0

    @parameter
    def diam(self):
        """Diameter of the cable model of this section (um)."""
        return 500.0

    @parameter
    def cm(self):
        """Specific membrane capacitance (uF/cm2)."""
        return 1.0

    @parameter
    def passive(self):
        """The leak mechanism, as pure data: NA for none, else {'g','e'}.

        ``serialize()`` cannot capture an inserted NEURON mechanism (it is
        an ``insert_passive`` side-effect, not a parameter), so the recipe
        records the leak *as data* and germinate re-applies it.
        """
        return NA

    @lazyfield
    def mechanisms(self):
        return []

    def germinate(self, model_class=SectionModel):
        """Build the live ``SectionModel`` from this recipe.

        The science->engine seam: make the model and its NEURON section,
        then chain the two engine-push steps (each returns ``self``):
        ``_push_morphology`` writes nseg/L/diam/cm into the live hoc, and
        ``insert_passive`` re-applies the leak the recipe records (a no-op
        when it records none). This method *is* the recipe/model boundary.
        """
        model = model_class(recipe=self)
        model.hoc = h.Section(name=self.name)
        return model._push_morphology(self).insert_passive()


class SimulationModel(Model):
    """A live NEURON simulation: the germinated body of a ``SimulationRecipe``."""
    def record_voltage(self, section_model, position=0.5):
        """Record membrane voltage at a segment over the run."""
        vec = h.Vector()
        vec.record(section_model(position)._ref_v)
        self._recordings[(section_model.name, position)] = vec
        return vec

    def run(self):
        """Run the simulation; return the recorded voltage vectors."""
        time = h.Vector()
        time.record(h._ref_t)
        h.finitialize(self.v_init)
        h.continuerun(self.tstop)
        return {
            "time": list(time),
            "recordings": {k: list(v) for k, v in self._recordings.items()},
        }

    @property
    def dt(self):
        return self.recipe.dt

    @property
    def tstop(self):
        return self.recipe.tstop

    @property
    def v_init(self):
        return self.recipe.v_init


class SimulationRecipe(ModelRecipe):
    """The pure science of a simulation run: time step, duration, init voltage."""
    @parameter
    def dt(self):
        """Simulation time step (ms)."""
        return 0.01

    @parameter
    def tstop(self):
        """Time to stop the simulation (ms)."""
        return 1000.0

    @tstop.validation
    def tstop(self, value):
        assert value > 0.0
        return value

    @parameter
    def v_init(self):
        """Initial voltage of the cell (mV)."""
        return -80.0

    def germinate(self, model_class=SimulationModel):
        """Build the live ``SimulationModel`` and arm the NEURON run loop."""
        h.load_file("stdrun.hoc")
        model = model_class(recipe=self)
        h.dt = self.dt
        model._recordings = {}
        return model


def build_soma():
    """Build the passive single-compartment soma specimen.

    Returns ``(sim, soma)`` — LIVE germinated models, configured but not
    yet run.
    """
    sim = SimulationRecipe(dt=0.025, v_init=-70.0, tstop=50.0).germinate()
    soma = SectionRecipe(
        name="soma", L=10.0, diam=10.0,
        passive={"g": 0.0001, "e": -70.0},
    ).germinate()
    return sim, soma


def receipt(soma):
    """The hashable receipt: NEURON's psection() for the soma."""
    return soma.hoc.psection()


if __name__ == "__main__":
    from pprint import pprint

    sim, soma = build_soma()
    print("soma descriptor values:")
    print("  L    =", soma.L)
    print("  diam =", soma.diam)
    print("  nseg =", soma.nseg)
    print("  cm   =", soma.cm)
    print("\nsim descriptor values:")
    print("  dt     =", sim.dt)
    print("  v_init =", sim.v_init)
    print("  tstop  =", sim.tstop)

    print("\nreceipt (psection):")
    pprint(receipt(soma))

    sim.record_voltage(soma, 0.5)
    result = sim.run()
    trace = result["recordings"][("soma", 0.5)]
    print("\nran %d steps; v[0]=%.4f  v[-1]=%.4f"
          % (len(trace), trace[0], trace[-1]))
    print("GREEN: recipe -> germinate -> NEURON -> run -> result")
