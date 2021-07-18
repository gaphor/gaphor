from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

version = subprocess.run(
    ["poetry", "version", "-s"], capture_output=True, text=True
).stdout.rstrip()

dir: Path = Path(__file__).resolve().parents[1]
dist: Path = dir / "dist"
Path(dist / "gaphor").mkdir(parents=True, exist_ok=True)

gaphor_dist: Path = dist / "gaphor"
seven_zip: Path = Path("C:/Program Files/7-Zip/7z.exe")
payload: Path = dist / "payload.7z"
portable: Path = dist / f"gaphor-{version}-portable"


def clean_files() -> None:
    print("Cleaning files")
    shutil.rmtree(portable, ignore_errors=True)
    payload.unlink(missing_ok=True)  # type: ignore[call-arg]


def build_installer() -> None:
    print("Building Installer")
    icon = dir / "windows" / "gaphor.ico"
    shutil.copy(icon, gaphor_dist / "gaphor.ico")
    os.chdir(gaphor_dist)
    subprocess.run(
        [
            "makensis",
            "-NOCD",
            f"-DVERSION={version}",
            str(dir / "windows" / "win_installer.nsi"),
        ],
        capture_output=True,
        text=True,
    )

    shutil.move(
        str(gaphor_dist / "gaphor-LATEST.exe"),
        dist / f"gaphor-{version}-installer.exe",
    )


def concatenate_files(input_files: list[Path], output_file: Path) -> None:
    for input_file in input_files:
        with open(input_file, "rb") as reader, open(output_file, "wb") as writer:
            data = reader.readlines()
            writer.writelines(data)


def unix2dos(file_path: Path) -> None:
    win_line_ending = b"\r\n"
    unix_line_ending = b"\n"

    with open(file_path, "rb") as open_file:
        content = open_file.read()
    content = content.replace(win_line_ending, unix_line_ending)
    with open(file_path, "wb") as open_file:
        open_file.write(content)


def build_portable_installer() -> None:
    print("Building portable installer")
    portable.mkdir(parents=True)
    shutil.copy(dir / "windows" / "gaphor.lnk", portable / "gaphor.lnk")
    shutil.copy(dir / "windows" / "README-PORTABLE.txt", portable / "README.txt")
    unix2dos(portable / "README.txt")
    config_path = portable / "config"
    config_path.mkdir()
    shutil.copytree(gaphor_dist, portable / "data")

    subprocess.run([str(seven_zip), "a", str(payload), str(portable)])
    concatenate_files(
        [seven_zip.parent / "7z.sfx", payload], dist / "gaphor-{version}-portable.exe"
    )


clean_files()
build_installer()
build_portable_installer()
clean_files()
print("Windows Installer builds are complete!")
