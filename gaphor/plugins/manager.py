"""A plugins manager."""

# Run pip via runpy: https://pip.pypa.io/en/stable/user_guide/#using-pip-from-your-program.

import argparse
import contextlib
import os
import runpy
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
    return run_pip("list", "--path", str(default_plugin_path()))


def install_plugin(args):
    path = default_plugin_path()
    path.mkdir(parents=True, exist_ok=True)

    return run_pip(
        "install",
        "--force-reinstall",
        "--target",
        str(path),
        args.name,
    )


def uninstall_plugin(args):
    return run_pip("uninstall", args.name)


def check_plugins(args):
    return run_pip("check")


@contextlib.contextmanager
def argv(*args):
    orig_argv = list(sys.argv)
    sys.argv = list(args)
    yield
    sys.argv = orig_argv


@contextlib.contextmanager
def pythonpath():
    if has_pythonpath := ("PYTHONPATH" in os.environ):
        orig_pythonpath = os.environ["PYTHONPATH"]
    os.environ["PYTHONPATH"] = str(default_plugin_path())
    yield
    if has_pythonpath:
        os.environ["PYTHONPATH"] = orig_pythonpath
    else:
        del os.environ["PYTHONPATH"]


def run_pip(*args):
    with pythonpath(), argv("pip", *args):
        try:
            runpy.run_module("pip", run_name="__main__")
        except SystemExit as se:
            return se.code
