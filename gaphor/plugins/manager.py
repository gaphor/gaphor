"""A plugins manager."""

import argparse
import subprocess
import sys


from gaphor.plugins import default_plugin_path


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
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "list", "--path", default_plugin_path()],
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
            path,
            args.name,
        ]
    )
    return completed.returncode


def uninstall_plugin(args):
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "uninstall", args.name],
        env={
            "PYTHONPATH": default_plugin_path(),
        },
    )
    return completed.returncode


def check_plugins(args):
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        env={
            "PYTHONPATH": default_plugin_path(),
        },
    )
    return completed.returncode
