"""
Install our schema:

    mkdir -p ~/.local/share/glib-2.0/schemas
    cp data/org.gaphor.Gaphor.gschema.xml ~/.local/share/glib-2.0/schemas/
    glib-compile-schemas ~/.local/share/glib-2.0/schemas/

"""
import argparse


def install_schemas_parser():
    parser = argparse.ArgumentParser(description="Install GSettings schema for Gaphor.")

    parser.set_defaults(command=install_schemas_command)

    return parser


def install_schemas_command(args):
    print("Installing schemas...")
