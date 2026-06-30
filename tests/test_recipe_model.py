"""The recipe/model contract — pinned without the engine.

These tests pin Shape B at the substrate level: a ``ModelRecipe`` is inert
(constructing it does not germinate), ``germinate()`` produces a distinct
live ``Model`` with the parameters replayed and a back-link to its recipe,
the recipe serializes to lean pure-science data with no engine state, and a
subclass ``germinate`` override is the method that runs. No NEURON needed —
the science→engine seam is exercised with a probe engine, so the contract
is provable anywhere.
"""
from descripy.model import ModelRecipe, Model
from descripy.param import parameter


class _ProbeRecipe(ModelRecipe):
    """A recipe whose 'engine' is a single flag, so we need no NEURON."""
    @parameter
    def k(self):
        return 7

    def germinate(self, model_class=Model):
        model = model_class(recipe=self)
        model.built = True               # the only thing germination does here
        model.k = self.k
        return model


def test_recipe_is_inert():
    """Constructing a recipe records science but does NOT germinate."""
    r = _ProbeRecipe(k=3)
    assert not hasattr(r, "built")       # construction did not build an engine
    assert r.k == 3                      # pure science is present


def test_germinate_produces_live():
    """germinate() returns a Model with replayed values and a recipe back-link."""
    r = _ProbeRecipe(k=3)
    m = r.germinate()
    assert isinstance(m, Model)
    assert m is not r                    # distinct object
    assert m.built and m.k == 3
    assert m.recipe is r                 # the model remembers its recipe


def test_recipe_serializes_without_engine():
    """The recipe serializes to lean pure-science data — no engine keys."""
    data = _ProbeRecipe(k=3).serialize()
    assert data == {"k": 3}              # only the science, nothing live


def test_base_germinate_replays_parameters():
    """The base germinate (no override) replays parameters onto a plain Model."""
    class _Plain(ModelRecipe):
        @parameter
        def a(self):
            return 1
        @parameter
        def b(self):
            return 2

    m = _Plain(a=10).germinate()
    assert isinstance(m, Model)
    assert m.a == 10 and m.b == 2        # parameter replay
    assert not hasattr(m, "built")       # base did not run the probe override
