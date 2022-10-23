import os
from pathlib import Path

import pyinstaller_versionfile

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

packaging_path = Path(__file__).resolve().parent


def get_version() -> str:
    project_dir = Path(__file__).resolve().parent.parent
    f = project_dir / "pyproject.toml"
    return str(tomllib.loads(f.read_text())["tool"]["poetry"]["version"])


def make_gaphor_script(gtk_version: str = os.getenv("GAPHOR_PKG_GTK", "4")):
    gaphor_script = packaging_path / "gaphor-script.py"
    with open(gaphor_script, "w") as file:

        # https://github.com/pyinstaller/pyinstaller/issues/6100
        # On one Windows computer, PyInstaller was adding a ; to
        # end of the path, this removes it if it exists
        file.write("import os\n")
        file.write("if os.environ['PATH'][-1] == ';':\n")
        file.write("    os.environ['PATH'] = os.environ['PATH'][:-1]\n")

        # Check for and remove two semicolons in path
        file.write("os.environ['PATH'] = os.environ['PATH'].replace(';;', ';')\n")

        file.write(f"os.environ['GAPHOR_USE_GTK'] = '{gtk_version}'\n")

        file.write("from gaphor.ui import main\n")
        file.write("import sys\n")
        file.write("main(sys.argv)\n")


def make_file_version_info():
    win_packaging_path = packaging_path / "windows"
    metadata = win_packaging_path / "versionfile_metadata.yml"
    file_version_out = win_packaging_path / "file_version_info.txt"

    version = get_version()
    if "dev" in version:
        version = version[: version.rfind(".dev")]

    pyinstaller_versionfile.create_versionfile_from_input_file(
        output_file=file_version_out,
        input_file=metadata,
        version=version,
    )
