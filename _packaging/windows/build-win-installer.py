# ruff: noqa: T201

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

version = subprocess.run(
    ["poetry", "version", "-s"], encoding="utf-8", capture_output=True, text=True
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
    shutil.copy(icon, files_to_package / "gaphor.ico")
    os.chdir(files_to_package)
    subprocess.run(
        [
            "makensis",
            "-NOCD",
            f"-DVERSION={version}",
            str(nsi),
        ],
        encoding="utf-8",
        capture_output=True,
        text=True,
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


def build_portable_installer(
    symlink_path: Path,
    readme_path: Path,
    files_to_package: Path,
    portable_path: Path,
    payload_path: Path,
    seven_zip_path: Path,
    output_file: Path,
) -> None:
    print("Building portable installer")
    shutil.copy(symlink_path, portable_path / symlink_path.name)
    shutil.copy(readme_path, portable_path / "README.txt")
    unix2dos(portable_path / "README.txt")
    config_path = portable_path / "config"
    config_path.mkdir()
    shutil.copytree(files_to_package, portable_path / "data")

    subprocess.run([str(seven_zip_path), "a", str(payload_path), str(portable_path)])
    if payload_path.is_file():
        print(f"Payload 7z archive found at {payload_path}")
    else:
        print("Payload 7z archive not found")
    sfx_path = seven_zip_path.parent / "7z.sfx"
    if sfx_path.is_file():
        print(f"Sfx file found at {sfx_path}")
    else:
        print("Sfx file not found")
    concatenate_files([seven_zip_path.parent / "7z.sfx", payload_path], output_file)


def main():
    working_dir: Path = Path(__file__).resolve().parents[1]
    dist: Path = working_dir / "dist"
    Path(dist / "gaphor").mkdir(parents=True, exist_ok=True)

    portable: Path = dist / f"gaphor-{version}-portable"
    payload: Path = dist / "payload.7z"

    clean_files([portable, payload])

    icon = working_dir / "windows" / "gaphor.ico"
    nsi = working_dir / "windows" / "win_installer.nsi"
    gaphor_files: Path = dist / "gaphor"
    installer = dist / f"gaphor-{version}-installer.exe"
    build_installer(icon, nsi, gaphor_files, installer)

    portable.mkdir(parents=True)
    symlink = working_dir / "windows" / "gaphor.lnk"
    readme = working_dir / "windows" / "README-PORTABLE.txt"
    seven_zip: Path = Path("C:/Program Files/7-Zip/7z.exe")
    installer = dist / f"gaphor-{version}-portable.exe"
    build_portable_installer(
        symlink, readme, gaphor_files, portable, payload, seven_zip, installer
    )

    clean_files([portable, payload])
    print("Windows Installer builds are complete!")


if __name__ == "__main__":
    main()
