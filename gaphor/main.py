import argparse
import logging
import sys

from gaphor.application import distribution

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main(argv=sys.argv) -> int:
    """Start Gaphor from the command line."""
    args = parse_args(argv)

    logging_config(args)

    if hasattr(args, "func"):
        return args.func(args)  # type: ignore[no-any-return]

    return ui(
        argv[0], args.model, args.self_test, args.profiler, args.gapplication_service
    )


def logging_config(args):
    if args.debug:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        logging.getLogger("gaphor").setLevel(logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


def execute_script(args) -> int:
    import runpy

    logging_config(args)
    script = args.script
    runpy.run_path(script, run_name="__main__")
    return 0


def export_script(args):
    print("Placeholder for diagram export")
    return 0


def ui(prog, models, self_test, profiler, gapplication_service) -> int:
    # Only now import the UI module
    from gaphor.ui import run

    run_argv = [prog]
    if self_test:
        run_argv += ["--self-test"]
    if gapplication_service:
        run_argv += ["--gapplication-service"]
    run_argv.extend(models)

    if profiler:
        import cProfile
        import pstats

        with cProfile.Profile() as profile:
            exit_code = profile.runcall(run, run_argv)

        profile_stats = pstats.Stats(profile)
        profile_stats.strip_dirs().sort_stats("time").print_stats(50)
        return exit_code

    return run(run_argv)


def parse_args(argv):
    parser = argparse.ArgumentParser(
        description="Gaphor is the simple modeling tool.",
        add_help=False,
    )

    parser.add_argument(
        "-v", "--version", help="print version and exit", nargs=0, action=VersionAction
    )

    parser.add_argument(
        "-d", "--debug", help="enable debug logging", action="store_true"
    )
    parser.add_argument(
        "-q", "--quiet", help="only show warning and error logging", action="store_true"
    )

    gui_parser = argparse.ArgumentParser(parents=[parser])
    gui_parser.add_argument(
        "-p", "--profiler", help="run in profiler (cProfile)", action="store_true"
    )
    gui_parser.add_argument(
        "--self-test", help="run self test and exit", action="store_true"
    )
    gui_parser.add_argument("--gapplication-service", action="store_true")
    gui_parser.add_argument("model", nargs="*", help="model file(s) to load")

    exec_parser = argparse.ArgumentParser(parents=[parser])
    exec_parser.add_argument("script", help="execute a script file and exit")
    exec_parser.set_defaults(func=execute_script)

    export_parser = argparse.ArgumentParser(parents=[parser])
    export_parser.set_defaults(func=export_script)

    commands = {
        "gui": gui_parser,
        "exec": exec_parser,
        "export": export_parser,
    }

    gui_parser.epilog = "extra commands: exec, export"

    args, extra_args = parser.parse_known_args(args=argv[1:])

    if extra_args and (cmd_parser := commands.get(extra_args[0])):
        cmd_parser.parse_args(extra_args[1:], namespace=args)
    else:
        gui_parser.parse_args(extra_args, namespace=args)

    return args


class VersionAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        print(f"Gaphor {distribution().version}")
        parser.exit()
