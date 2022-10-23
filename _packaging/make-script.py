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
