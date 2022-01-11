from pathlib import Path
import time
import tomli
from PyInstaller.utils.hooks import copy_metadata

block_cipher = None


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
    return str(tomli.loads(f.read_text())["tool"]["poetry"]["version"])


a = Analysis(
    ["gaphor-script.py"],
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
        ("../LICENSE.txt", "gaphor"),
        ("../gaphor/locale/*", "gaphor/locale"),
        ("../gaphor/templates/*.gaphor", "gaphor/templates"),
    ]
    + glade_files
    + ui_files
    + copy_metadata("gaphor")
    + copy_metadata("gaphas"),
    hiddenimports=[],
    hooksconfig={
        "gi": {
            "module-versions": {
                "GtkSource": "4",
            },
        },
    },
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
    info_plist={
        "CFBundleVersion": get_version(),
        "NSHumanReadableCopyright": f"Copyright 2001-{time.strftime('%Y')} Gaphor Developers, Apache 2 License.",
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
