# Run PyInstaller with this script from the project root directory

import os
from pathlib import Path

import tomllib

import pyinstaller_versionfile
from packaging.version import Version
from PyInstaller.utils.hooks import collect_entry_point, copy_metadata

block_cipher = None

COPYRIGHT = f"Copyright © 2001 The Gaphor Development Team."

ROOT = Path.cwd()

svg_files = [(p, p.relative_to(ROOT).parent) for p in (ROOT / "gaphor").rglob("*.svg")]
ui_files = [(p, p.relative_to(ROOT).parent) for p in (ROOT / "gaphor").rglob("*.ui")]
mo_files = [
    (p, p.relative_to(ROOT).parent) for p in (ROOT / "gaphor" / "locale").rglob("*.mo")
]


def get_version() -> Version:
    f = ROOT / "pyproject.toml"
    return Version(tomllib.loads(f.read_text(encoding="utf-8"))["project"]["version"])


def collect_entry_points(*names):
    hidden_imports = []
    for entry_point in names:
        _datas, imports = collect_entry_point(entry_point)
        hidden_imports.extend(imports)
    return hidden_imports


a = Analysis(  # type: ignore
    [ROOT / "gaphor" / "__main__.py"],
    pathex=[ROOT],
    binaries=[],
    datas=[
        (ROOT / "gaphor/diagram.css", "gaphor"),
        (ROOT / "gaphor/ui/styling*.css", "gaphor/ui"),
        (ROOT / "gaphor/ui/placement-icon-base.png", "gaphor/ui"),
        (ROOT / "gaphor/ui/language-specs/*.lang", "gaphor/ui/language-specs"),
        (ROOT / "LICENSES/Apache-2.0.txt", "gaphor"),
        (ROOT / "gaphor/templates/*.gaphor", "gaphor/templates"),
        (
            ROOT / "gaphor/ui/installschemas/org.gaphor.Gaphor.gschema.xml",
            "share/glib-2.0/schemas",
        ),
    ]
    + svg_files
    + ui_files
    + mo_files
    + copy_metadata("gaphor"),
    hiddenimports=collect_entry_points(
        "gaphor.argparsers",
        "gaphor.services",
        "gaphor.appservices",
        "gaphor.modelinglanguages",
        "gaphor.modules",
    )
    + ["_cffi_backend", "babel.numbers"],
    hooksconfig={
        "gi": {
            "module-versions": {
                "Gtk": "4.0",
                "GtkSource": "5",
            },
        },
    },
    hookspath=[ROOT / "_packaging"],
    runtime_hooks=[
        ROOT / "_packaging" / "fix_path.py",
        ROOT / "_packaging" / "pydot_patch.py",
    ],
    excludes=["FixTk", "tcl", "tk", "_tkinter", "tkinter", "Tkinter"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)  # type: ignore

ver = get_version()
pyinstaller_versionfile.create_versionfile(
    output_file=ROOT / "build" / "windows_file_version_info.txt",
    version=f"{ver.major}.{ver.minor}.{ver.micro}.0",
    company_name="Gaphor",
    file_description="Gaphor",
    internal_name="Gaphor",
    legal_copyright=COPYRIGHT,
    original_filename="gaphor.exe",
    product_name="Gaphor",
)

exe = EXE(  # type: ignore
    pyz,
    a.scripts,
    options=[],
    exclude_binaries=True,
    name="gaphor",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    icon=ROOT / "_packaging" / "windows" / "gaphor.ico",
    version=ROOT / "build" / "windows_file_version_info.txt",
    console=False,
    codesign_identity=os.getenv("CODESIGN_IDENTITY"),
    entitlements_file=ROOT / "_packaging" / "macos" / "entitlements.plist",
)
coll = COLLECT(  # type: ignore
    exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, name="gaphor"
)
app = BUNDLE(  # type: ignore
    coll,
    name="Gaphor.app",
    icon=ROOT / "_packaging/macos/gaphor.icns",
    bundle_identifier="org.gaphor.gaphor",
    version=str(get_version()),
    info_plist={
        "CFBundleVersion": str(get_version()),
        "NSHumanReadableCopyright": COPYRIGHT,
        "LSMinimumSystemVersion": "10.15",
        "NSHighResolutionCapable": True,
        "NSSupportsAutomaticGraphicsSwitching": True,
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
                "UTTypeConformsTo": ["public.xml"],
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
        "NSRequiresAquaSystemAppearance": False,
        "NSAppleScriptEnabled": False,
    },
)
