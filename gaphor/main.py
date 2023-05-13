import argparse
import logging
import sys

from gaphor.application import distribution

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main(argv=sys.argv) -> int:
    """Start Gaphor from the command line."""

    logging_config()

    args = parse_args(argv)

    if args.profiler:
        import cProfile
        import pstats

        with cProfile.Profile() as profile:
            exit_code: int = profile.runcall(args.func, args)

        profile_stats = pstats.Stats(profile)
        profile_stats.strip_dirs().sort_stats("time").print_stats(50)
        return exit_code

    return args.func(args)  # type: ignore[no-any-return]


def parse_args(argv):
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "-v", "--version", help="print version and exit", nargs=0, action=VersionAction
    )

    loglevel = parser.add_mutually_exclusive_group()
    loglevel.add_argument(
        "-d",
        "--debug",
        help="enable debug logging",
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
        "-p", "--profiler", help="run in profiler (cProfile)", action="store_true"
    )

    commands = {
        "exec": exec_parser,
        "export": export_parser,
    }

    args, extra_args = parser.parse_known_args(args=argv[1:])

    if extra_args and (command := commands.get(extra_args[0])):
        cmd, *extra_args = extra_args
        p = command()
        cmd_parser = argparse.ArgumentParser(
            description=p.description,
            prog=f"{parser.prog} {cmd}",
            parents=[parser, p],
            add_help=False,
        )

    else:
        p = gui_parser()
        cmd_parser = argparse.ArgumentParser(
            description=p.description,
            prog=f"{parser.prog} [command]",
            parents=[parser, p],
            add_help=False,
        )
        cmd_parser.epilog = f"commands: {', '.join(commands)}"

    return cmd_parser.parse_args(extra_args, namespace=args)


def gui_parser():
    def run(args) -> int:
        # Only now import the UI module
        import gaphor.ui

        run_argv = [sys.argv[0]]
        if args.self_test:
            run_argv += ["--self-test"]
        if args.gapplication_service:
            run_argv += ["--gapplication-service"]
        run_argv.extend(args.model)

        return gaphor.ui.run(run_argv)

    parser = argparse.ArgumentParser()
    parser.description = "Gaphor is the simple modeling tool."
    parser.add_argument(
        "--self-test", help="run self test and exit", action="store_true"
    )
    parser.add_argument("--gapplication-service", action="store_true")
    parser.add_argument("model", nargs="*", help="model file(s) to load")
    parser.set_defaults(func=run)
    return parser


def exec_parser():
    def execute_script(args) -> int:
        import runpy

        script = args.script
        runpy.run_path(script, run_name="__main__")
        return 0

    parser = argparse.ArgumentParser()
    parser.description = "Execute a python script from within Gaphor."
    parser.add_argument("script", help="execute a script file and exit")
    parser.set_defaults(func=execute_script)
    return parser


def export_parser():
    def export_script(args) -> int:
        print("Placeholder for diagram export")
        return 0

    parser = argparse.ArgumentParser()
    parser.description = "Export diagrams from a Gaphor model."
    parser.set_defaults(func=export_script)
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
        print(f"Gaphor {distribution().version}")
        parser.exit()


class LogLevelAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        logging_config(self.const)
