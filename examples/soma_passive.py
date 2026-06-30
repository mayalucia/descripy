"""The single-compartment passive soma — descripy's first crucible.

Distilled from the teaching workbook
``~/work/bbp/work/bravlibpy/learn/cells/simulation.org`` (the Oren Amsalem
single-compartment specimen at its line 775), reduced to *passive-only* so
that it runs against NEURON built-ins alone (no compiled NMODL).

What this exercises, end to end:

    descriptor (@parameter + @validation)  ->  live NEURON object (self.hoc)
        ->  run the simulation             ->  a result (psection() receipt)

This is the loop descripy's "descriptor-as-seed" thesis is about: a value
is not merely stored, it is *bound to the live object it configures*, and
the configured object yields a receipt we can hash and compare.

Run (NEURON is bound to the py311 interpreter on this machine)::

    /Users/vishalsoodmuchu/.vmgr_repo/py311/bin/python examples/soma_passive.py
"""
from descripy.config import parameter, lazyfield, Config

from neuron import h


class Section(Config):
    """A section of a neuronal cell, backed by a live NEURON Section.

    Each ``@parameter`` carries a default (the method body) and a
    ``@x.validation`` hook that pushes the resolved value into the live
    ``self.hoc`` object. That hook is the seam where a *recorded belief*
    becomes a *running configuration*.
    """
    def __init__(self, name, **fields):
        self.name = name
        self.hoc = h.Section(name=name)
        super().__init__(**fields)

    @parameter
    def nseg(self):
        """Number of segments to model in this section."""
        return 1

    @nseg.validation
    def nseg(self, value):
        if value is not None:
            self.hoc.nseg = value
        return value

    @parameter
    def L(self):
        """Length of section (um)."""
        return 20.0

    @L.validation
    def L(self, value):
        if value is not None:
            self.hoc.L = value
        return value

    @parameter
    def diam(self):
        """Diameter of the cable model of this section (um)."""
        return 500.0

    @diam.validation
    def diam(self, value):
        if value is not None:
            self.hoc.diam = value
        return value

    @parameter
    def cm(self):
        """Specific membrane capacitance (uF/cm2)."""
        return 1.0

    @cm.validation
    def cm(self, value):
        if value is not None:
            self.hoc.cm = value
        return value

    @lazyfield
    def mechanisms(self):
        return []

    def segment(self, position):
        """Access a segment at a relative position (0 < value < 1)."""
        return self.hoc(position)

    def __call__(self, position):
        """Access a segment in this section (e.g. ``soma(0.5)``)."""
        return self.hoc(position)

    def insert_passive(self, g=0.001, e=-70.0):
        """Insert NEURON's built-in passive (leak) mechanism."""
        self.hoc.insert("pas")
        for seg in self.hoc:
            seg.pas.g = g
            seg.pas.e = e
        return self


class Simulation(Config):
    """Configure and run a NEURON simulation."""
    def __init__(self, *args, **kwargs):
        h.load_file("stdrun.hoc")
        self._recordings = {}
        super().__init__(*args, **kwargs)

    @parameter
    def dt(self):
        """Simulation time step (ms)."""
        return 0.01

    @dt.validation
    def dt(self, value):
        h.dt = value
        return value

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

    def record_voltage(self, section, position=0.5):
        """Record membrane voltage at a segment over the run."""
        vec = h.Vector()
        vec.record(section(position)._ref_v)
        self._recordings[(section.name, position)] = vec
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


def build_soma():
    """Build the passive single-compartment soma specimen.

    Returns ``(sim, soma)`` configured but not yet run.
    """
    sim = Simulation(dt=0.025, v_init=-70.0, tstop=50.0)
    soma = Section("soma", L=10.0, diam=10.0)
    soma.insert_passive(g=0.0001, e=-70.0)
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
    print("GREEN: descriptor -> NEURON -> run -> result")
