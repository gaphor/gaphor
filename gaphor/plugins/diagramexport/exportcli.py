#!/usr/bin/python

import argparse
import logging
import re
from pathlib import Path
from typing import List

from gaphor.application import Session
from gaphor.core.modeling import Diagram
from gaphor.diagram.export import escape_filename, save_pdf, save_png, save_svg
from gaphor.storage import storage

log = logging.getLogger(__name__)


def pkg2dir(package):
    """Return directory path from package class."""
    name: List[str] = []
    while package:
        name.insert(0, package.name)
        package = package.package
    return "/".join(name)


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
        choices=["pdf", "svg", "png"],
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

        for diagram in factory.select(Diagram):
            odir = pkg2dir(diagram.owner)

            # just diagram name
            dname = escape_filename(diagram.name)
            # full diagram name including package path
            pname = f"{odir}/{dname}"

            if args.underscores:
                odir = odir.replace(" ", "_")
                dname = dname.replace(" ", "_")

            if name_re and not name_re.search(pname):
                log.debug("skipping %s", pname)
                continue

            if args.dir:
                odir = f"{args.dir}/{odir}"

            outfilename = f"{odir}/{dname}.{args.format}"

            if not Path(odir).exists():
                log.debug("creating dir %s", odir)
                Path(odir).mkdir(parents=True)

            log.debug("rendering: %s -> %s...", pname, outfilename)

            if args.format == "pdf":
                save_pdf(outfilename, diagram)
            elif args.format == "svg":
                save_svg(outfilename, diagram)
            elif args.format == "png":
                save_png(outfilename, diagram)
            else:
                raise RuntimeError(f"Unknown file format: {args.format}")
