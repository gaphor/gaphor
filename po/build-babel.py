import subprocess
from pathlib import Path

po_path: Path = Path(__file__).resolve().parent


def run_babel(command: str, input: Path, output_file: Path, locale: str):
    subprocess.run(
        [
            "pybabel",
            command,
            f"--input={str(input)}",
            f"--output-file={str(output_file)}",
            f"--locale={str(locale)}",
            "--domain=gaphor",
        ]
    )


def update_po_files():
    pot_path = po_path / "gaphor.pot"
    for path in (path for path in po_path.iterdir() if path.suffix == ".po"):
        run_babel("update", pot_path, path, path.stem)


def compile_mo_files():
    for path in (path for path in po_path.iterdir() if path.suffix == ".po"):
        mo_path = po_path.parent / "locale" / path.stem / "LC_MESSAGES" / "gaphor.mo"
        mo_path.parent.mkdir(parents=True, exist_ok=True)
        run_babel("compile", path, mo_path, path.stem)


if __name__ == "__main__":
    update_po_files()
    compile_mo_files()
