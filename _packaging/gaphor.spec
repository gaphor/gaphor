import logging
import os
import time
from pathlib import Path

import pyinstaller_versionfile
from PyInstaller.utils.hooks import copy_metadata, collect_entry_point

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib


logging.getLogger(__name__).info(
    f"Target GTK version: {os.getenv('GAPHOR_PKG_GTK', '4')}"
)


block_cipher = None

COPYRIGHT = f"Copyright © 2001-{time.strftime('%Y')} Arjan J. Molenaar and Dan Yeaw."

glade_files = [
    (str(p), str(Path(*p.parts[1:-1]))) for p in Path("../gaphor").rglob("*.glade")
]
ui_files = [
    (str(p), str(Path(*p.parts[1:-1]))) for p in Path("../gaphor").rglob("*.ui")
]


def get_version() -> str:
    project_dir = Path.cwd().parent
    print(project_dir.resolve())
    f = project_dir / "pyproject.toml"
    return str(tomllib.loads(f.read_text())["tool"]["poetry"]["version"])


def get_semver_version() -> str:
    version = get_version()
    return version[: version.rfind(".dev")] if "dev" in version else version


def collect_entry_points(*names):
    hidden_imports = []
    for entry_point in names:
        _datas, imports = collect_entry_point(entry_point)
        hidden_imports.extend(imports)
    return hidden_imports


a = Analysis(
    ["../gaphor/__main__.py"],
    pathex=["../"],
    binaries=[],
    datas=[
        ("../gaphor/ui/layout.xml", "gaphor/ui"),
        ("../gaphor/ui/styling*.css", "gaphor/ui"),
        ("../gaphor/ui/*.png", "gaphor/ui"),
        (
            "../gaphor/ui/icons/hicolor/scalable/actions/*.svg",
            "gaphor/ui/icons/hicolor/scalable/actions",
        ),
        (
            "../gaphor/ui/icons/hicolor/scalable/apps/*.svg",
            "gaphor/ui/icons/hicolor/scalable/apps",
        ),
        (
            "../gaphor/ui/icons/hicolor/scalable/emblems/*.svg",
            "gaphor/ui/icons/hicolor/scalable/emblems",
        ),
        ("../gaphor/ui/language-specs/*.lang", "gaphor/ui/language-specs"),
        ("../LICENSE.txt", "gaphor"),
        ("../gaphor/locale/*", "gaphor/locale"),
        ("../gaphor/templates/*.gaphor", "gaphor/templates"),
    ]
    + glade_files
    + ui_files
    + copy_metadata("gaphor")
    + copy_metadata("gaphas"),
    hiddenimports=collect_entry_points(
        "gaphor.services",
        "gaphor.appservices",
        "gaphor.modelinglanguages",
        "gaphor.modules",
    ),
    hooksconfig={
        "gi": {
            "module-versions": {
                "Gtk": "3.0" if os.getenv("GAPHOR_PKG_GTK") == "3" else "4.0",
                "GtkSource": "4" if os.getenv("GAPHOR_PKG_GTK") == "3" else "5",
            },
        },
    },
    hookspath=["."],
    runtime_hooks=[
        f"use_gtk_{os.getenv('GAPHOR_PKG_GTK', '4')}.py",
        "fix_path.py",
        "pydot_patch.py",
    ],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

pyinstaller_versionfile.create_versionfile(
    output_file="windows/file_version_info.txt",
    version=get_semver_version(),
    company_name="Gaphor",
    file_description="Gaphor",
    internal_name="Gaphor",
    legal_copyright=COPYRIGHT,
    original_filename="gaphor-exe.exe",
    product_name="Gaphor",
)

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
    codesign_identity=os.getenv("CODESIGN_IDENTITY"),
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
    info_plist={
        "CFBundleVersion": get_version(),
        "NSHumanReadableCopyright": COPYRIGHT,
        "LSMinimumSystemVersion": "10.13",
        "NSHighResolutionCapable": True,
        "LSApplicationCategoryType": "public.app-category.developer-tools",
        "NSPrincipalClass": "NSApplication",
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeExtensions": ["gaphor"],
                "CFBundleTypeIconFile": "gaphor.icns",
                "CFBundleTypeMIMETypes": ["application/x-gaphor"],
                "CFBundleTypeName": "Gaphor Model",
                "CFBundleTypeOSTypes": ["GAPHOR"],
                "CFBundleTypeRole": "Editor",
                "LSIsAppleDefaultForType": True,
                "LSItemContentTypes": ["org.gaphor.model"],
            }
        ],
        "UTExportedTypeDeclarations": [
            {
                "UTTypeIdentifier": "org.gaphor.model",
                "UTTypeConformsTo": ["gaphor.model"],
                "UTTypeDescription": "Gaphor Model",
                "UTTypeIconFile": "gaphor.icns",
                "UTTypeReferenceURL": "https://gaphor.org",
                "UTTypeTagSpecification": {
                    "com.apple.ostype": "GAPHOR",
                    "public.filename-extension": ["gaphor"],
                    "public.mime-type": ["application/x-gaphor"],
                },
            }
        ],
        "NSDesktopFolderUsageDescription": "Gaphor needs your permission to load models from disk.",
        "NSDocumentsFolderUsageDescription": "Gaphor needs your permission to load models from disk.",
        "NSDownloadsFolderUsageDescription": "Gaphor needs your permission to load models from disk.",
        "NSRequiresAquaSystemAppearance": "No",
        "NSAppleScriptEnabled": False,
    },
)
