from PyInstaller.utils.hooks import copy_metadata
from pathlib import Path
from tomlkit import parse

block_cipher = None

project_dir = Path.cwd()

glade_files = [
    (str(p), str(Path(*p.parts[1:-1])))
    for p in project_dir.rglob("*.glade")
]
ui_files = [
    (str(p), str(Path(*p.parts[1:-1])))
    for p in project_dir.rglob("*.ui")
]


def get_version() -> str:
    f = project_dir / "pyproject.toml"
    return str(parse(f.read_text())["tool"]["poetry"]["version"])


a = Analysis(
    ["gaphor-script.py"],
    pathex=["../"],
    binaries=[],
    datas=[
        ("../gaphor/ui/layout.xml", "gaphor/ui"),
        ("../gaphor/ui/layout.css", "gaphor/ui"),
        ("../gaphor/ui/*.png", "gaphor/ui"),
        ("../gaphor/services/helpservice/*.svg", "gaphor/services/helpservice"),
        (
            "../gaphor/ui/icons/hicolor/scalable/actions/*.svg",
            "gaphor/ui/icons/hicolor/scalable/actions",
        ),
        ("../LICENSE.txt", "gaphor"),
        ("../gaphor/locale/*", "gaphor/locale"),
    ]
    + glade_files
    + ui_files
    + copy_metadata("gaphor")
    + copy_metadata("gaphas"),
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["lib2to3", "tcl", "tk", "_tkinter", "tkinter", "Tkinter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    options=[],
    exclude_binaries=True,
    name="gaphor-exe",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    icon="windows/gaphor.ico",
    version="windows/file_version_info.txt",
    console=False,
    codesign_identity="Developer ID Application: Daniel Yeaw (Z7V37BLNR9)",
    entitlements_file="macos/entitlements.plist",
)
coll = COLLECT(
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="gaphor"
)
app = BUNDLE(
    coll,
    name="Gaphor.app",
    icon="macos/gaphor.icns",
    bundle_identifier="org.gaphor.gaphor",
    version=get_version(),
)
