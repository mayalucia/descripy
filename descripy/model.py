"""The recipe and the model — pure science, and its live germination.

This is the carve of the old ``Config`` into the two things it conflated
(EPISTEMOLOGY.org Part A, "seed records intent; germination re-derives
consequence"):

  - ``ModelRecipe`` — an *inert, serializable* description of the science:
    the chosen ``parameter`` values and nested ``section``s, and nothing
    of the engine that will run them. Constructing a recipe touches no
    NEURON (no ``hoc``); it only records intent. It is the seed.

  - ``Model`` — the *live* object a recipe germinates into: it holds the
    engine state (e.g. a NEURON ``Section``) and knows how to run. It is
    the consequence.

They are joined by ``recipe.germinate() -> Model``. The base
``germinate`` replays the recipe's parameters onto a fresh ``Model``;
each model author *overrides* it to add the engine-specific build steps
(build the ``hoc``, push morphology, insert mechanisms). That override is
the science→engine seam — the place the soma example used to call "the
seam where a recorded belief becomes a running configuration." In the old
fused ``Config`` that seam was smeared across ``__init__`` and the
``@validation`` push-hooks, firing at construction time because
construction *was* germination. Splitting the lifecycle splits the code:
the pure half of validation (cast + check) stays on the recipe; the
engine-push half moves into ``germinate``.

The run-receipt that the old ``Config`` also carried (``status`` /
``output`` / ``update``) is *not* here: it is neither pure science nor
the live object but a record of a run — a future ``Task``, parked in
``_attic/task.py`` until a real run-consumer earns it (the same
build-by-use discipline that deferred ``status.py`` and ``serialize.py``).
"""
from descripy.struct import serialize_value, field, section, Struct
from descripy.param import parameter

from lazy import lazy


class ModelRecipe(Struct):
    """An inert, serializable record of the science: parameters + sections.

    Constructable without the engine; ``serialize()`` gives the lean seed;
    ``germinate()`` builds the live ``Model``.
    """
    @field
    def label(self):
        """..."""
        return self.__class__.__name__

    @lazy
    def parameters(self):
        """Parameters defined in this recipe subclass `cls`.
        """
        return self.collect_elements(of_type=parameter)

    @lazy
    def sections(self):
        """Sections defined in this recipe subclass `cls`.
        """
        return self.collect_elements(of_type=section)

    def get_parameter(self, p):
        """..."""
        value = self.get_element(p, of_type=parameter)
        assert not isinstance(value, Struct),(
            "A nested `ModelRecipe` / `Struct` instance must not be a parameter,"
            " but a section")
        return value

    @lazy
    def parameter_values(self):
        """Collect parameters of this recipe into a dictionary.
        """
        return {p: self.get_parameter(p) for p in self.parameters}

    def get_section(self, s, element_types=None):
        """..."""
        value = self.get_element(s, of_type=section)
        assert isinstance(value, Struct),(
            "A section must be a `Struct` / `ModelRecipe` instance.")

        element_types = element_types or [field]
        return {k: v for et in element_types
                for k, v in value.get_element_values(of_type=et).items()}


    def _serialize_sections(self, keep_na):
        """..."""
        sections = {s: self.get_element(s, of_type=section) for s in self.sections}
        return {section.storage_name(n): sxn.serialize(keep_na)
                for n, sxn in sections.items()}

    def serialize(self, dropna=True, to_output=None):
        """..."""
        data = {p: serialize_value(v, na=("null" if not dropna else None))
                for p, v in self.parameter_values.items()}
        data.update(self._serialize_sections(dropna))

        data = {k: v for k, v in data.items() if v is not None}

        if not to_output:
            return data
        return to_output(data)

    def germinate(self, model_class=None):
        """Build the live ``Model`` this recipe describes.

        Base behaviour: replay the recipe's parameters onto a fresh model.
        The live partner is chosen at germination time via ``model_class``
        (defaulting to the plain ``Model``), so one recipe can germinate
        into different live bodies — a test double here, the real engine
        model there. Engine-specific build steps (build the ``hoc``, push
        morphology, insert mechanisms) belong in a subclass override — that
        override is the science→engine seam.
        """
        model = (model_class or Model)(recipe=self)
        model._replay_parameters(self.parameter_values)
        return model


class Model:
    """The live object a ``ModelRecipe`` germinates into.

    Holds the engine state and knows how to run. The base only carries the
    originating recipe and the replayed parameter values; engine state and
    ``run()`` live on subclasses.
    """
    def __init__(self, recipe):
        self.recipe = recipe

    def _replay_parameters(self, values):
        """Copy the recipe's resolved parameter values onto this model."""
        for name, value in values.items():
            setattr(self, name, value)
