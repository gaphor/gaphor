"""CLI command for generating an HTML model report."""

import argparse
import logging

import gaphor.storage as storage
from gaphor.application import Session
from gaphor.plugins.htmlreport.generator import generate_report

log = logging.getLogger(__name__)


def html_report_parser():
    parser = argparse.ArgumentParser(
        description="Generate an HTML report from a Gaphor model."
    )

    parser.add_argument(
        "-o",
        "--dir",
        metavar="directory",
        help="output directory for the report",
        default="report",
    )
    parser.add_argument("model", nargs="+")
    parser.set_defaults(command=html_report_command)

    return parser


def html_report_command(args):
    session = Session(
        services=[
            "event_manager",
            "component_registry",
            "element_factory",
            "element_dispatcher",
            "modeling_language",
        ]
    )
    factory = session.get_service("element_factory")
    modeling_language = session.get_service("modeling_language")

    for model in args.model:
        log.info("Loading model %s", model)
        with open(model, encoding="utf-8") as file_obj:
            storage.load(file_obj, factory, modeling_language)

    log.info("Generating HTML report to %s", args.dir)
    generate_report(factory, args.dir)
    log.info("Done.")
