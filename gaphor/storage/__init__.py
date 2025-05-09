"""Load and save Gaphor models to Gaphors own XML format.

Three functions are exported: `load(file_obj)`loads a model from a
file. `save(file_obj)` stores the current model in a file.
"""

__all__ = [
    "load",
    "load_generator",
    "save",
    "save_generator",
    "UnknownModelElementError",
]

from gaphor.storage.load import UnknownModelElementError, load, load_generator
from gaphor.storage.save import save, save_generator
