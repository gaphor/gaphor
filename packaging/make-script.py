import sys
from pathlib import Path

import pyinstaller_versionfile
import tomlkit

packaging_path = Path(__file__).resolve().parent


def get_version() -> str:
    project_dir = Path(__file__).resolve().parent.parent
    f = project_dir / "pyproject.toml"
    return str(tomlkit.parse(f.read_text())["tool"]["poetry"]["version"])


def make_gaphor_script():
    pyproject_toml = packaging_path.parent / "pyproject.toml"
    with open(pyproject_toml) as f:
        toml = tomlkit.parse(f.read())

    gaphor_script = packaging_path / "gaphor-script.py"
    with open(gaphor_script, "w") as file:
        plugins = toml["tool"]["poetry"]["plugins"]
        for cat in plugins.values():
            for entrypoint in cat.values():
                file.write(f"import {entrypoint.split(':')[0]}\n")

        file.write("from gaphor.ui import main\n")
        file.write("import sys\n")
        file.write("main(sys.argv)\n")


def make_file_version_info():
    win_packaging_path = packaging_path / "windows"
    metadata = win_packaging_path / "versionfile_metadata.yml"
    file_version_out = win_packaging_path / "file_version_info.txt"

    pyinstaller_versionfile.create_versionfile_from_input_file(
        output_file=file_version_out,
        input_file=metadata,
        version=get_version(),
    )
