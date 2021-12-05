"""Test if models are up to date."""

from pathlib import Path

from gaphor.C4Model import c4model
from gaphor.codegen.coder import main
from gaphor.core.modeling import coremodel
from gaphor.RAAML import raaml
from gaphor.SysML import sysml
from gaphor.UML import uml


def test_core_model(tmp_path):
    outfile = tmp_path / "coremodel.py"
    main(
        modelfile="models/Core.gaphor",
        overridesfile="models/Core.override",
        outfile=outfile,
    )

    current_model = Path(coremodel.__file__).read_text()
    generated_model = outfile.read_text()

    assert current_model == generated_model


def test_uml_model(tmp_path):
    outfile = tmp_path / "uml.py"
    main(
        modelfile="models/UML.gaphor",
        overridesfile="models/UML.override",
        supermodelfiles=[("gaphor.core.modeling.coremodel", "models/Core.gaphor")],
        outfile=outfile,
    )

    current_model = Path(uml.__file__).read_text()
    generated_model = outfile.read_text()

    assert current_model == generated_model


def test_c4model_model(tmp_path):
    outfile = tmp_path / "c4model.py"
    main(
        modelfile="models/C4Model.gaphor",
        supermodelfiles=[("gaphor.UML.uml", "models/UML.gaphor")],
        outfile=outfile,
    )

    current_model = Path(c4model.__file__).read_text()
    generated_model = outfile.read_text()

    assert current_model == generated_model


def test_sysml_model(tmp_path):
    outfile = tmp_path / "sysml.py"
    main(
        modelfile="models/SysML.gaphor",
        supermodelfiles=[
            ("gaphor.core.modeling.coremodel", "models/Core.gaphor"),
            ("gaphor.UML.uml", "models/UML.gaphor"),
        ],
        outfile=outfile,
    )

    current_model = Path(sysml.__file__).read_text()
    generated_model = outfile.read_text()

    assert current_model == generated_model


def test_raaml_model(tmp_path):
    outfile = tmp_path / "raaml.py"
    main(
        modelfile="models/RAAML.gaphor",
        supermodelfiles=[
            ("gaphor.core.modeling.coremodel", "models/Core.gaphor"),
            ("gaphor.UML.uml", "models/UML.gaphor"),
            ("gaphor.SysML.sysml", "models/SysML.gaphor"),
        ],
        outfile=outfile,
    )

    current_model = Path(raaml.__file__).read_text()
    generated_model = outfile.read_text()

    assert current_model == generated_model
