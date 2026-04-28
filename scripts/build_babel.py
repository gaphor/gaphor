# ruff: noqa: T201
"""Babel gettext helpers for Gaphor."""

import json
import subprocess
import sys
import urllib.request
from pathlib import Path

po_path: Path = Path(__file__).resolve().parent.parent / "po"
RELEASE_MATURE_LOCALES_FILE = po_path / "release_mature_locales.json"

WEBLATE_TRANSLATIONS_URL = (
    "https://hosted.weblate.org/api/components/gaphor/gaphor/translations/"
    "?page_size=100"
)


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


def _fetch_mature_locales(first_url: str, min_percent: float) -> set[str]:
    """Return language codes at or above *min_percent* from the Weblate API.

    Exits the process with status 1 on network or parse errors.
    """
    codes: set[str] = set()
    url: str | None = first_url
    try:
        while url:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.load(resp)
            for row in payload.get("results", []):
                if row.get("is_source"):
                    continue
                code: str = row.get("language_code") or ""
                if code and float(row.get("translated_percent") or 0.0) >= min_percent:
                    codes.add(code)
            url = payload.get("next") or None
    except (OSError, json.JSONDecodeError) as e:
        print(f"Error: Weblate API request failed: {e}", file=sys.stderr)
        raise SystemExit(1) from None
    if not codes:
        print("Error: Weblate returned no mature locales.", file=sys.stderr)
        raise SystemExit(1)
    return codes


def update_release_mature_locales_file() -> None:
    """Fetch Weblate stats and write ``po/release_mature_locales.json``.

    Called by the monthly ``release-mature-locales-updater`` workflow
    (``poetry run poe release-mature-locales-update``).

    To change the threshold, edit ``min_translated_percent`` in
    ``po/release_mature_locales.json`` and commit the change.
    """
    data = json.loads(RELEASE_MATURE_LOCALES_FILE.read_text(encoding="utf-8"))
    min_pct = float(data.get("min_translated_percent", 72.0))

    from_api = _fetch_mature_locales(WEBLATE_TRANSLATIONS_URL, min_pct)
    po_stems = {p.stem for p in po_path.iterdir() if p.suffix == ".po"}
    chosen = sorted(from_api & po_stems)
    if not chosen:
        print(
            "Error: No intersection between Weblate mature locales and po/*.po.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    new_text = (
        json.dumps({"min_translated_percent": min_pct, "locales": chosen}, indent=2)
        + "\n"
    )
    if RELEASE_MATURE_LOCALES_FILE.read_text(encoding="utf-8") == new_text:
        print("No change to po/release_mature_locales.json")
        return
    RELEASE_MATURE_LOCALES_FILE.write_text(new_text, encoding="utf-8")
    print(f"Wrote {RELEASE_MATURE_LOCALES_FILE} with {len(chosen)} locale(s).")


def release_language_codes() -> frozenset[str]:
    """Locales to compile for official release binaries.

    Read from ``po/release_mature_locales.json``, which is updated by the
    monthly ``release-mature-locales-updater`` workflow via
    ``poetry run poe release-mature-locales-update``.
    """
    data = json.loads(RELEASE_MATURE_LOCALES_FILE.read_text(encoding="utf-8"))
    po_stems = {p.stem for p in po_path.iterdir() if p.suffix == ".po"}
    return frozenset(data["locales"]) & po_stems


def compile_mo_release():
    mature_translations = release_language_codes()
    for path in po_path.iterdir():
        if path.suffix == ".po" and path.stem in mature_translations:
            compile_mo_file(path)


if __name__ == "__main__":
    update_po_files()
    compile_mo_all()
