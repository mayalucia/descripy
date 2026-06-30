"""Configurations for computational analyses — now a compatibility shim.

The class that was ``Config`` has been carved into ``ModelRecipe`` (pure
science) and ``Model`` (its live germination) in ``descripy/model.py``,
with the run-receipt cluster parked as ``Task`` in ``_attic/task.py``.
``Config`` survives here only as an alias for ``ModelRecipe`` to ease the
migration; new code should import from ``descripy.model``.
"""
from descripy.model import ModelRecipe, Model
from descripy.param import parameter, ParamError
from descripy.struct import lazyfield

#: deprecated alias — ``Config`` was the fused recipe+model+receipt.
Config = ModelRecipe
