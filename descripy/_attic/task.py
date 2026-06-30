"""Task — the run-receipt, parked until a real run-consumer earns it.

When ``Config`` was carved into ``ModelRecipe`` (pure science) and
``Model`` (the live object), a third cluster was left over: ``status``,
``output``, and ``update()`` — what came of *running* the thing. That is
neither the science nor the live object; it is a record of a run. The
right name for it is ``Task``, and the right time to build it is when a
real dispatch/run consumer needs the receipt — not before (the
build-by-use discipline from EPISTEMOLOGY.org that also deferred
``status.py`` and ``serialize.py``).

The examples already carry the de-facto run-receipt this stub anticipates:
``examples/soma_seed.py``'s ``expect`` (the receipt the seed must
reproduce) and ``Believed.outcome`` (which points at it). When ``Task``
is finally built, it should subsume those — a Task is a Model that was
run, carrying the receipt it produced and the belief about it.

This stub holds the old ``Config`` receipt members verbatim so the design
is not lost. It is reachable only by explicit ``descripy._attic.task``
import and is deliberately NOT re-exported by ``descripy/__init__.py``.
"""
from descripy.struct import Struct
from descripy.param import parameter
from descripy.nothing import NA


class Task(Struct):
    """A record of a run: the receipt cluster lifted off the old ``Config``.

    Parked, not wired. Build by use when a real run-consumer appears.
    """
    @parameter
    def status(self):
        """Status of the task this configures.
        Has it been run? Was the result successful?
        The default of NA / None indicates the configuration has not been
        used for any task yet.
        If used, a copy can be attached to the result of the task; the
        value of this parameter may depend on the particular subclass.
        Furthermore, output sections may be added, or set to non-NA values
        that describe the result of running the task.
        """
        return NA

    @parameter
    def output(self):
        """Location where the output of running this should go.
        """
        return NA

    def update(self, status=None, output=None):
        """..."""
        fields = self.serialize()
        if status: fields["status"] = status
        if output: fields["output"] = output
        return self.__class__(fields)
