"""
Install our schema:

    mkdir -p ~/.local/share/glib-2.0/schemas
    cp data/org.gaphor.Gaphor.gschema.xml ~/.local/share/glib-2.0/schemas/
    glib-compile-schemas ~/.local/share/glib-2.0/schemas/

"""
import argparse
import shutil
import subprocess
from pathlib import Path

from gi.repository import GLib


def install_schemas_parser():
    parser = argparse.ArgumentParser(description="Install GSettings schema for Gaphor.")

    default_schema_dir = Path(GLib.get_user_data_dir()) / "glib-2.0" / "schemas"
    parser.add_argument(
        "--schemas-dir",
        dest="schemas_dir",
        metavar="path",
        default=default_schema_dir,
        help="installation directory for GSettings schemas",
    )
    parser.add_argument(
        "--glib-compile-schemas",
        dest="glib_compile_schemas",
        metavar="path",
        default="glib-compile-schemas",
        help="path to glib-compile-schemas",
    )
    parser.set_defaults(command=install_schemas_command)

    return parser


def install_schemas_command(args):
    schemas_dir = Path(args.schemas_dir)
    # Print, since logger is not initialized at this point
    print(f"Installing Gaphor schema in {schemas_dir}…")  # noqa: T201
    schemas_dir.mkdir(parents=True, exist_ok=True)
    schema_file = Path(__file__).parent / "org.gaphor.Gaphor.gschema.xml"
    shutil.copy(schema_file, schemas_dir)
    subprocess.run([args.glib_compile_schemas, str(schemas_dir)])
