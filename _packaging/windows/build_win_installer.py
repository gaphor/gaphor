# ruff: noqa: T201

from __future__ import annotations

import platform
import shutil
import subprocess
from pathlib import Path

version = subprocess.run(
    ["poetry", "version", "-s"],
    encoding="utf-8",
    capture_output=True,
    text=True,
    check=True,
).stdout.rstrip()


def clean_files(paths: list[Path]) -> None:
    print("Cleaning files")
    for path in paths:
        if path.is_dir():
            shutil.rmtree(path, ignore_errors=True)
        elif path.is_file():
            path.unlink(missing_ok=True)


def build_installer(
    icon: Path, nsi: Path, files_to_package: Path, output_file: Path
) -> None:
    print("Building Installer")
    if (
        not (files_to_package / "gaphor.exe").exists()
        and not (files_to_package / "gaphor").exists()
    ):
        raise SystemExit(
            "dist/gaphor does not contain PyInstaller output. "
            "Run 'poe package' first to build the application."
        )
    shutil.copy(icon, files_to_package / "gaphor.ico")
    # Pass absolute path to NSIS - File /r uses script dir by default, not cwd
    source_dir = files_to_package.resolve()
    subprocess.run(
        [
            "makensis",
            "-NOCD",
            f"-DVERSION={version}",
            f"-DGAPHOR_SOURCE={source_dir}",
            str(nsi),
        ],
        encoding="utf-8",
        capture_output=True,
        text=True,
        check=True,
        cwd=source_dir,
    )

    shutil.move(str(files_to_package / "gaphor-LATEST.exe"), output_file)


def concatenate_files(input_files: list[Path], output_file: Path) -> None:
    print(f"Opening {output_file} for write")
    with output_file.open("wb") as writer:
        for input_file in input_files:
            print(f"Writing {input_file}")
            with input_file.open("rb") as reader:
                shutil.copyfileobj(reader, writer)


def unix2dos(file_path: Path) -> None:
    win_line_ending = b"\r\n"
    unix_line_ending = b"\n"

    with file_path.open("rb") as open_file:
        content = open_file.read()
    content = content.replace(win_line_ending, unix_line_ending)
    with file_path.open("wb") as open_file:
        open_file.write(content)


def find_7zip() -> tuple[Path, Path]:
    """Find 7-Zip executable and SFX module for the current platform."""
    if platform.system() == "Windows":
        seven_zip = Path("C:/Program Files/7-Zip/7z.exe")
        sfx = seven_zip.parent / "7z.sfx"
    else:
        # Linux/macOS: use p7zip (apt install p7zip-full)
        seven_zip_path = shutil.which("7z")
        if not seven_zip_path:
            raise SystemExit(
                "7-Zip is required for portable installer but '7z' was not found in PATH. "
                "Install p7zip-full (e.g. apt install p7zip-full on Debian/Ubuntu)."
            )
        seven_zip = Path(seven_zip_path)
        # p7zip places SFX in /usr/lib/p7zip/ (Ubuntu/Debian) or /usr/lib64/p7zip/ (Fedora)
        sfx_candidates = [
            seven_zip.parent / "7z.sfx",
            Path("/usr/lib/p7zip/7zCon.sfx"),
            Path("/usr/lib/p7zip/7z.sfx"),
            Path("/usr/lib/x86_64-linux-gnu/p7zip/7zCon.sfx"),
            Path("/usr/lib64/p7zip/7zCon.sfx"),
            Path("/usr/lib64/p7zip/7z.sfx"),
        ]
        sfx = next((p for p in sfx_candidates if p.is_file()), None)
        if not sfx:
            # Fallback: search for 7zCon.sfx under /usr/lib*
            for candidate in Path("/usr/lib").rglob("7zCon.sfx"):
                if candidate.is_file():
                    sfx = candidate
                    break
            if not sfx and Path("/usr/lib64").exists():
                for candidate in Path("/usr/lib64").rglob("7zCon.sfx"):
                    if candidate.is_file():
                        sfx = candidate
                        break
        if not sfx:
            raise SystemExit(
                "7z.sfx / 7zCon.sfx not found. Install p7zip-full (apt install p7zip-full)."
            )
    return seven_zip, sfx


def build_portable_installer(
    symlink_path: Path,
    readme_path: Path,
    files_to_package: Path,
    portable_path: Path,
    payload_path: Path,
    seven_zip_path: Path,
    sfx_path: Path,
    output_file: Path,
) -> None:
    print("Building portable installer")
    shutil.copy(symlink_path, portable_path / symlink_path.name)
    shutil.copy(readme_path, portable_path / "README.txt")
    unix2dos(portable_path / "README.txt")
    config_path = portable_path / "config"
    config_path.mkdir()
    shutil.copytree(files_to_package, portable_path / "data")

    subprocess.run(
        [str(seven_zip_path), "a", str(payload_path), str(portable_path)], check=True
    )
    if payload_path.is_file():
        print(f"Payload 7z archive found at {payload_path}")
    else:
        print("Payload 7z archive not found")
    print(f"Sfx file at {sfx_path}")
    concatenate_files([sfx_path, payload_path], output_file)


def main():
    working_dir: Path = Path.cwd()
    dist: Path = working_dir / "dist"
    Path(dist / "gaphor").mkdir(parents=True, exist_ok=True)

    portable: Path = dist / f"gaphor-{version}-portable"
    payload: Path = dist / "payload.7z"

    clean_files([portable, payload])

    icon = working_dir / "_packaging" / "windows" / "gaphor.ico"
    nsi = working_dir / "_packaging" / "windows" / "win_installer.nsi"
    gaphor_files: Path = dist / "gaphor"
    installer = dist / f"gaphor-{version}-installer.exe"
    build_installer(icon, nsi, gaphor_files, installer)

    portable.mkdir(parents=True)
    symlink = working_dir / "_packaging" / "windows" / "gaphor.lnk"
    readme = working_dir / "_packaging" / "windows" / "README-PORTABLE.txt"
    seven_zip, sfx_path = find_7zip()
    installer = dist / f"gaphor-{version}-portable.exe"
    build_portable_installer(
        symlink, readme, gaphor_files, portable, payload, seven_zip, sfx_path, installer
    )

    clean_files([portable, payload])
    print("Windows Installer builds are complete!")


if __name__ == "__main__":
    main()
