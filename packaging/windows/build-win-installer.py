import os
import shutil
import subprocess
from pathlib import Path

version = subprocess.run(
    ["poetry", "version", "-s"], capture_output=True, text=True
).stdout.rstrip()

dir = Path(__file__).resolve().parents[1]
Path(dir / "dist" / "gaphor").mkdir(parents=True, exist_ok=True)

dist_location = dir / "dist" / "gaphor"
seven_zip = Path("C:/Program Files/7-Zip/7z.exe")
makensis = Path("C:/Program Files (x86)/NSIS/makensis.exe")
payload = dir / "dist" / "payload.7z"
portable = dir / "dist" / f"gaphor-{version}-portable"

MINGW = "mingw64"


def clean_files():
    print("Cleaning files")
    shutil.rmtree(portable, ignore_errors=True)
    if payload.is_file:
        payload.unlink()


def build_installer():
    print("Building Installer")
    icon = dir / "windows" / "gaphor.ico"
    shutil.copy(icon, dist_location / "gaphor.ico")
    os.chdir(dist_location)
    subprocess.run(
        [
            str(makensis),
            "-NOCD",
            f"-DVERSION={version}",
            str(dir / "windows" / "win_installer.nsi"),
        ],
        capture_output=True,
        text=True,
    )

    shutil.move(
        str(dist_location / "gaphor-LATEST.exe"),
        dir / "dist" / f"gaphor-{version}-installer.exe",
    )


def concatenate_files(input_files, output_file):
    for input_file in input_files:
        with open(input_file, "rb") as reader, open(output_file, "wb") as writer:
            data = reader.readlines()
            writer.writelines(data)


def unix2dos(file_path):
    win_line_ending = b"\r\n"
    unix_line_ending = b"\n"

    with open(file_path, "rb") as open_file:
        content = open_file.read()
    content = content.replace(win_line_ending, unix_line_ending)
    with open(file_path, "wb") as open_file:
        open_file.write(content)


def build_portable_installer():
    print("Building portable installer")
    portable.mkdir(parents=True)
    shutil.copy(dir / "windows" / "gaphor.lnk", portable / "gaphor.lnk")
    shutil.copy(dir / "windows" / "README-PORTABLE.txt", portable / "README.txt")
    unix2dos(portable / "README.txt")
    config_path = portable / "config"
    config_path.mkdir()
    shutil.copytree(dist_location, portable / "data")

    subprocess.run([str(seven_zip), "a", str(payload), str(portable)])
    concatenate_files([seven_zip.parent / "7z.sfx", payload], f"{portable}.exe")


clean_files()
build_installer()
build_portable_installer()
clean_files()
print("Windows Installer builds are complete!")
