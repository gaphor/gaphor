"""Test if models are up to date."""

import functools
from pathlib import Path

import pytest

from gaphor.C4Model import c4model
from gaphor.codegen import coder
from gaphor.codegen.coder import main
from gaphor.core.modeling import coremodel
from gaphor.RAAML import raaml
from gaphor.SysML import sysml
from gaphor.UML import uml


@pytest.fixture(scope="session", autouse=True)
def cache_loaded_models():
    """Speed up testing by caching loaded models."""
    coder.load_model = functools.lru_cache(maxsize=None)(coder.load_model)


def test_core_model(tmp_path):
    outfile = tmp_path / "coremodel.py"
    main(
        modelfile="models/Core.gaphor",
        overridesfile="models/Core.override",
        outfile=outfile,
    )

    current_model = Path(coremodel.__file__).read_text(encoding="utf-8")
    generated_model = outfile.read_text(encoding="utf-8")

    assert generated_model == current_model


def test_uml_model(tmp_path):
    outfile = tmp_path / "uml.py"
    main(
        modelfile="models/UML.gaphor",
        overridesfile="models/UML.override",
        supermodelfiles=[("Core", "models/Core.gaphor")],
        outfile=outfile,
    )

    current_model = Path(uml.__file__).read_text(encoding="utf-8")
    generated_model = outfile.read_text(encoding="utf-8")

    assert generated_model == current_model


def test_c4model_model(tmp_path):
    outfile = tmp_path / "c4model.py"
    main(
        modelfile="models/C4Model.gaphor",
        supermodelfiles=[("Core", "models/Core.gaphor"), ("UML", "models/UML.gaphor")],
        outfile=outfile,
    )

    current_model = Path(c4model.__file__).read_text(encoding="utf-8")
    generated_model = outfile.read_text(encoding="utf-8")

    assert generated_model == current_model


def test_sysml_model(tmp_path):
    outfile = tmp_path / "sysml.py"
    main(
        modelfile="models/SysML.gaphor",
        overridesfile="models/SysML.override",
        supermodelfiles=[
            ("Core", "models/Core.gaphor"),
            ("UML", "models/UML.gaphor"),
        ],
        outfile=outfile,
    )

    current_model = Path(sysml.__file__).read_text(encoding="utf-8")
    generated_model = outfile.read_text(encoding="utf-8")

    assert generated_model == current_model


def test_raaml_model(tmp_path):
    outfile = tmp_path / "raaml.py"
    main(
        modelfile="models/RAAML.gaphor",
        supermodelfiles=[
            ("Core", "models/Core.gaphor"),
            ("UML", "models/UML.gaphor"),
            ("SysML", "models/SysML.gaphor"),
        ],
        outfile=outfile,
    )

    current_model = Path(raaml.__file__).read_text(encoding="utf-8")
    generated_model = outfile.read_text(encoding="utf-8")

    assert generated_model == current_model
