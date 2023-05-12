import argparse
import logging
import sys

from gaphor.application import distribution

LOG_FORMAT = "%(name)s %(levelname)s %(message)s"


def main(argv) -> int:
    """Start Gaphor from the command line.  This function creates an option
    parser for retrieving arguments and options from the command line.  This
    includes a Gaphor model to load.

    The application is then initialized, passing along the option
    parser.  This provides plugins and services with access to the
    command line options and may add their own.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v", "--version", help="Print version and exit", action="store_true"
    )
    parser.add_argument("-d", "--debug", help="Debug output", action="store_true")
    parser.add_argument("-q", "--quiet", help="Quiet output", action="store_true")
    parser.add_argument(
        "-p", "--profiler", help="Run in profiler (cProfile)", action="store_true"
    )
    parser.add_argument(
        "--self-test", help="Run self test and exit", action="store_true"
    )
    parser.add_argument(
        "--gapplication-service",
        help="Enter GApplication service mode (use from D-Bus service files)",
        action="store_true",
    )
    parser.add_argument("filename", nargs="*", help="Model(s) to load")

    args = parser.parse_args(args=argv[1:])

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

    return ui(
        argv[0], args.filename, args.self_test, args.profiler, args.gapplication_service
    )


def ui(prog, filenames, self_test, profiler, gapplication_service) -> int:
    # Only now import the UI module
    from gaphor.ui import run

    run_argv = [prog]
    if self_test:
        run_argv += ["--self-test"]
    if gapplication_service:
        run_argv += ["--gapplication-service"]
    run_argv.extend(filenames)

    if profiler:
        import cProfile
        import pstats

        with cProfile.Profile() as profile:
            exit_code = profile.runcall(run, run_argv)

        profile_stats = pstats.Stats(profile)
        profile_stats.strip_dirs().sort_stats("time").print_stats(50)
        return exit_code

    return run(run_argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
