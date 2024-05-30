import argparse
import logging
import os
import sys

from gaphor.application import distribution
from gaphor.entrypoint import initialize
from gaphor.plugins import default_plugin_path, enable_plugins

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main(argv=None) -> int:
    """Start Gaphor from the command line."""

    if argv is None:
        argv = sys.argv
    logging_config()

    with enable_plugins(default_plugin_path()):
        commands: dict[str, argparse.ArgumentParser] = initialize("gaphor.argparsers")

        args = parse_args(argv[1:], commands)

        return run_profiler(args) if args.profiler else args.command(args)  # type: ignore[no-any-return]


def run_profiler(args):
    import cProfile
    import pstats

    with cProfile.Profile() as profile:
        exit_code: int = profile.runcall(args.command, args)

    profile_stats = pstats.Stats(profile)
    profile_stats.strip_dirs().sort_stats("time").print_stats(50)
    return exit_code


def parse_args(args: list[str], commands: dict[str, argparse.ArgumentParser]):
    defaults = default_parser()
    parser = argparse.ArgumentParser(
        description="Gaphor is the simple modeling tool.",
        epilog="Thank you for using Gaphor <https://gaphor.org>.",
        parents=[version_parser()],
    )
    subparsers = parser.add_subparsers(
        title="subcommands (default: gui)",
        description=f"Get help for commands with {prog()} COMMAND --help.",
    )

    active_parser = parser
    for name, cmd_parser in commands.items():
        sp = subparsers.add_parser(
            name,
            description=cmd_parser.description,
            help=(cmd_parser.description or "").lower().rstrip("."),
            parents=[defaults, cmd_parser],
            add_help=False,
        )

        # Special case: fall back to gui subcommand if none is provided
        if name == "gui" and not (args and args[0] in commands):
            # Workaround: show toplevel help on the gui subcommand
            sp.format_help = parser.format_help  # type: ignore[method-assign]
            active_parser = sp

    return active_parser.parse_args(args)


def version_parser():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "-V", "--version", help="print version and exit", nargs=0, action=VersionAction
    )
    return parser


def default_parser():
    parser = argparse.ArgumentParser(add_help=False)

    loglevel = parser.add_mutually_exclusive_group()
    loglevel.add_argument(
        "-v",
        "--verbose",
        help="enable verbose logging",
        nargs=0,
        action=LogLevelAction,
        const=logging.DEBUG,
    )
    loglevel.add_argument(
        "-q",
        "--quiet",
        help="only show warning and error logging",
        nargs=0,
        action=LogLevelAction,
        const=logging.WARNING,
    )
    parser.add_argument(
        "--profiler", help="run in profiler (cProfile)", action="store_true"
    )
    return parser


def gui_parser():
    def run(args) -> int:
        # Only now import the UI module
        import gaphor.ui

        # Recreate a command line for our GTK gui
        run_argv = [sys.argv[0]]
        if args.gapplication_service:
            run_argv += ["--gapplication-service"]
        run_argv.extend(args.model)

        return gaphor.ui.run(run_argv, recover=True)

    parser = argparse.ArgumentParser(
        description="Launch the GUI.", parents=[version_parser()]
    )

    group = parser.add_argument_group("options (no command provided)")
    group.add_argument("--gapplication-service", action="store_true")
    group.add_argument("model", nargs="*", help="model file(s) to load")
    parser.set_defaults(command=run)
    return parser


def self_test_parser():
    def run(args) -> int:
        # Only now import the UI module
        import gaphor.ui

        # Recreate a command line for our GTK gui
        run_argv = [sys.argv[0]]

        return gaphor.ui.run(run_argv, launch_service="self_test")

    parser = argparse.ArgumentParser(
        description="Perform a self test and exit", parents=[version_parser()]
    )

    parser.set_defaults(command=run)
    return parser


def exec_parser():
    def execute_script(args) -> int:
        import runpy

        script = args.script
        runpy.run_path(script, run_name="__main__")
        return 0

    parser = argparse.ArgumentParser(
        description="Execute a python script from within Gaphor."
    )
    parser.add_argument("script", help="execute a script file and exit")
    parser.set_defaults(command=execute_script)
    return parser


def logging_config(level=logging.INFO):
    if level <= logging.DEBUG:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, force=True)
        logging.getLogger("gaphor").setLevel(logging.DEBUG)
    elif level >= logging.WARNING:
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT, force=True)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT, force=True)


class VersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(f"Gaphor {distribution().version}")  # noqa: T201
        parser.exit()


class LogLevelAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        logging_config(self.const)


def prog():
    return os.path.basename(sys.argv[0])
