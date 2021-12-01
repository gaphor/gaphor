"""Test if models are up to date."""

from pathlib import Path

from gaphor.codegen.coder import main
from gaphor.UML import uml


def test_uml_model(tmp_path):
    outfile = tmp_path / "uml.py"
    main(
        modelfile="models/UML.gaphor",
        overridesfile="models/UML.override",
        outfile=outfile,
    )

    current_model = Path(uml.__file__).read_text()
    generated_model = outfile.read_text()

    assert current_model == generated_model
