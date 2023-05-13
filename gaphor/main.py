import argparse
import logging
import sys

from gaphor.application import distribution

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main(argv=sys.argv) -> int:
    """Start Gaphor from the command line."""
    args = parse_args(argv)

    if args.version:
        print(f"Gaphor {distribution().version}")
        return 0

    if args.debug:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
        logging.getLogger("gaphor").setLevel(logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(level=logging.WARNING, format=LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

    if args.script:
        return execute_script(args.script)

    return ui(
        argv[0], args.model, args.self_test, args.profiler, args.gapplication_service
    )


def execute_script(script: str) -> int:
    import runpy

    runpy.run_path(script, run_name="__main__")
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
    parser = argparse.ArgumentParser(description="Gaphor is the simple modeling tool.")
    parser.add_argument(
        "-v", "--version", help="print version and exit", action="store_true"
    )
    parser.add_argument(
        "-d", "--debug", help="enable debug logging", action="store_true"
    )
    parser.add_argument(
        "-q", "--quiet", help="only show warning and error logging", action="store_true"
    )

    exec_group = parser.add_argument_group("scripting options")
    exec_group.add_argument(
        "--exec", help="execute a script file and exit", dest="script", metavar="script"
    )

    ui_group = parser.add_argument_group("interactive (GUI) options")
    ui_group.add_argument(
        "-p", "--profiler", help="run in profiler (cProfile)", action="store_true"
    )
    ui_group.add_argument(
        "--self-test", help="run self test and exit", action="store_true"
    )
    ui_group.add_argument("model", nargs="*", help="model file(s) to load")

    gapplication_group = parser.add_argument_group(
        "GApplication settings (use from D-Bus service files)"
    )
    gapplication_group.add_argument("--gapplication-service", action="store_true")

    return parser.parse_args(args=argv[1:])


if __name__ == "__main__":
    sys.exit(main())
