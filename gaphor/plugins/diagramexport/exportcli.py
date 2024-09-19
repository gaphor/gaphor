#!/usr/bin/python

import argparse
import logging
import re

from gaphor.application import Session
from gaphor.diagram.export import save_eps, save_pdf, save_png, save_svg
from gaphor.plugins.diagramexport.exportall import export_all
from gaphor.storage import storage

log = logging.getLogger(__name__)


def export_parser():
    parser = argparse.ArgumentParser(description="Export diagrams from a Gaphor model.")

    parser.add_argument(
        "-u",
        "--use-underscores",
        dest="underscores",
        action="store_true",
        help="use underscores instead of spaces for output filenames",
    )
    parser.add_argument(
        "-o", "--dir", metavar="directory", help="output to directory", default="."
    )
    parser.add_argument(
        "-f",
        "--format",
        metavar="format",
        help="output file format, default pdf",
        default="pdf",
        choices=["pdf", "svg", "png", "eps"],
    )
    parser.add_argument(
        "-r",
        "--regex",
        dest="regex",
        metavar="regex",
        help="process diagrams which name matches given regular expression;"
        " name includes package name; regular expressions are case insensitive",
    )
    parser.add_argument("model", nargs="+")
    parser.set_defaults(command=export_command)

    return parser


def export_command(args):
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

    name_re = re.compile(args.regex, re.IGNORECASE) if args.regex else None
    # we should have some gaphor files to be processed at this point
    for model in args.model:
        log.debug("loading model %s", model)
        with open(model, encoding="utf-8") as file_obj:
            storage.load(file_obj, factory, modeling_language)
        log.debug("ready for rendering")

        out_fn = None
        if args.format == "pdf":
            out_fn = save_pdf
        elif args.format == "svg":
            out_fn = save_svg
        elif args.format == "png":
            out_fn = save_png
        elif args.format == "eps":
            out_fn = save_eps
        else:
            raise RuntimeError(f"Unknown file format: {args.format}")

        export_all(factory, args.dir, out_fn, args.format, name_re, args.underscores)
