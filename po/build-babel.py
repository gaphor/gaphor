import subprocess
from pathlib import Path

po_path: Path = Path(__file__).resolve().parent


def run_babel(command: str, input: Path, output_file: Path, locale: str):
    subprocess.run(
        [
            "pybabel",
            command,
            f"--input={input}",
            f"--output-file={output_file}",
            f"--locale={locale}",
            "--domain=gaphor",
        ],
        check=True,
    )


def update_po_files():
    pot_path = po_path / "gaphor.pot"
    for path in (path for path in po_path.iterdir() if path.suffix == ".po"):
        run_babel("update", pot_path, path, path.stem)


def compile_mo_file(path: Path):
    mo_path = (
        po_path.parent / "gaphor" / "locale" / path.stem / "LC_MESSAGES" / "gaphor.mo"
    )
    mo_path.parent.mkdir(parents=True, exist_ok=True)
    run_babel("compile", path, mo_path, path.stem)


def compile_mo_all():
    for path in (path for path in po_path.iterdir() if path.suffix == ".po"):
        compile_mo_file(path)


def compile_mo_release():
    mature_translations = [
        "cs",
        "es",
        "de",
        "nl",
        "fi",
        "hr",
        "hu",
        "pt_BR",
        "ru",
        "tr",
        "zh_hans",
    ]
    for path in (
        path
        for path in po_path.iterdir()
        if path.stem in mature_translations and path.suffix == ".po"
    ):
        compile_mo_file(path)


if __name__ == "__main__":
    update_po_files()
    compile_mo_all()
