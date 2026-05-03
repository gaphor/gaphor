from __future__ import annotations

import re
from pathlib import Path

UML_IMPORT_PATTERN = re.compile(r"\bgaphor\.UML\b")


def _python_files(directory: Path) -> list[Path]:
    return sorted(p for p in directory.rglob("*.py") if "__pycache__" not in p.parts)


def test_kerml_and_sysml2_have_no_direct_uml_dependencies():
    project_root = Path(__file__).resolve().parents[3]
    scoped_dirs = [
        project_root / "gaphor" / "KerML",
        project_root / "gaphor" / "SysML2",
    ]

    violations: list[str] = []
    for scoped_dir in scoped_dirs:
        for py_file in _python_files(scoped_dir):
            text = py_file.read_text(encoding="utf-8")
            if UML_IMPORT_PATTERN.search(text):
                rel_path = py_file.relative_to(project_root)
                violations.append(str(rel_path))

    assert not violations, (
        "Found direct UML dependency in KerML/SysML2 modules: " + ", ".join(violations)
    )
