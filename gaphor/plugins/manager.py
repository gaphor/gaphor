"""A plugins manager."""

import argparse
import subprocess
import sys


from gaphor.plugins import default_plugin_path
from gaphor.main import prog


def parser():
    parser = argparse.ArgumentParser(description="Plugin related subcommands.")

    subparser = parser.add_subparsers(
        title="plugin subcommands",
        description=f"Get help for plugin commands with {prog()} plugin COMMAND --help.",
    )

    list_parser = subparser.add_parser(
        "list",
        description="List all installed plugin packages.",
        help="list all installed plugin packages",
    )
    list_parser.set_defaults(command=list_plugins)

    install_parser = subparser.add_parser(
        "install",
        description="Install plugin packages from pypi.",
        help="install plugin packages",
    )
    install_parser.add_argument("name")
    install_parser.set_defaults(command=install_plugin)

    uninstall_parser = subparser.add_parser(
        "uninstall",
        description="Uninstall packages from the plugin folder.",
        help="uninstalled plugin modules",
    )
    uninstall_parser.add_argument("name")
    uninstall_parser.set_defaults(command=uninstall_plugin)

    check_parser = subparser.add_parser(
        "check",
        description="Check plugin package dependencies.",
        help="check plugin package dependencies",
    )
    check_parser.set_defaults(command=check_plugins)

    parser.set_defaults(command=lambda _: parser.print_usage())

    return parser


def list_plugins(args):
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--path", str(default_plugin_path())],
        capture_output=True,
    )
    print(completed.stdout)
    if completed.stderr:
        print("--- stderr ---", file=sys.stderr)
        print(completed.stderr, file=sys.stderr)
    return completed.returncode


def install_plugin(args):
    path = default_plugin_path()
    path.mkdir(parents=True, exist_ok=True)

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "--force-reinstall",
            "--target",
            str(path),
            args.name,
        ]
    )
    return completed.returncode


def uninstall_plugin(args):
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", args.name],
        env={
            "PYTHONPATH": str(default_plugin_path()),
        },
    )
    return completed.returncode


def check_plugins(args):
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        env={
            "PYTHONPATH": str(default_plugin_path()),
        },
    )
    return completed.returncode
