"""A plugins manager."""

import argparse
import subprocess
import sys
import pathlib

from gi.repository import GLib

PLUGIN_PATH = pathlib.Path(GLib.get_user_state_dir(), "gaphor-plugins-2")
PLUGIN_PATH.mkdir(parents=True, exist_ok=True)


def parser():
    parser = argparse.ArgumentParser(description="Export diagrams from a Gaphor model.")

    subparser = parser.add_subparsers(title="plugin subcommands")

    list_parser = subparser.add_parser(
        "list", description="list all installed plugin modules"
    )
    list_parser.set_defaults(command=list_plugins)

    install_parser = subparser.add_parser(
        "install", description="install plugin modules"
    )
    install_parser.add_argument("name")
    install_parser.set_defaults(command=install_plugin)

    uninstall_parser = subparser.add_parser(
        "uninstall", description="uninstalled plugin modules"
    )
    uninstall_parser.add_argument("name")
    uninstall_parser.set_defaults(command=uninstall_plugin)

    check_parser = subparser.add_parser(
        "check", description="check plugin module dependencies"
    )
    check_parser.set_defaults(command=check_plugins)

    parser.set_defaults(command=lambda _: parser.print_usage())

    return parser


def list_plugins(args):
    subprocess.run([sys.executable, "-m", "pip", "list", "--path", PLUGIN_PATH])


def install_plugin(args):
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--target", PLUGIN_PATH, args.name]
    )


def uninstall_plugin(args):
    subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", args.name],
        env={
            "PYTHONPATH": PLUGIN_PATH,
        },
    )


def check_plugins(args):
    subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        env={
            "PYTHONPATH": PLUGIN_PATH,
        },
    )
