#!/usr/bin/python

import optparse
import os
import re
import sys
from typing import List

from gaphor.application import Session
from gaphor.core.modeling import Diagram
from gaphor.plugins.diagramexport import save_pdf, save_png, save_svg
from gaphor.storage import storage


def pkg2dir(package):
    """Return directory path from package class."""
    name: List[str] = []
    while package:
        name.insert(0, package.name)
        package = package.package
    return "/".join(name)


def parse_options(argv):

    usage = "usage: %prog [options] file1 file2..."

    parser = optparse.OptionParser(usage=usage)

    parser.add_option(
        "-v", "--verbose", dest="verbose", action="store_true", help="verbose output"
    )
    parser.add_option(
        "-u",
        "--use-underscores",
        dest="underscores",
        action="store_true",
        help="use underscores instead of spaces for output filenames",
    )
    parser.add_option(
        "-d", "--dir", dest="dir", metavar="directory", help="output to directory"
    )
    parser.add_option(
        "-f",
        "--format",
        dest="format",
        metavar="format",
        help="output file format, default pdf",
        default="pdf",
        choices=["pdf", "svg", "png"],
    )
    parser.add_option(
        "-r",
        "--regex",
        dest="regex",
        metavar="regex",
        help="process diagrams which name matches given regular expression;"
        " name includes package name; regular expressions are case insensitive",
    )

    options, args = parser.parse_args(argv)

    if not args:
        parser.print_help()

    return options, args


def main(argv=sys.argv[1:]):

    options, args = parse_options(argv)

    def message(msg):
        if options.verbose:
            print(msg, file=sys.stderr)

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

    name_re = None
    if options.regex:
        name_re = re.compile(options.regex, re.I)

    # we should have some gaphor files to be processed at this point
    for model in args:
        message(f"loading model {model}")
        storage.load(model, factory, modeling_language)
        message("ready for rendering")

        for diagram in factory.select(Diagram):
            odir = pkg2dir(diagram.owner)

            # just diagram name
            dname = diagram.name
            # full diagram name including package path
            pname = f"{odir}/{dname}"

            if options.underscores:
                odir = odir.replace(" ", "_")
                dname = dname.replace(" ", "_")

            if name_re and not name_re.search(pname):
                message(f"skipping {pname}")
                continue

            if options.dir:
                odir = f"{options.dir}/{odir}"

            outfilename = f"{odir}/{dname}.{options.format}"

            if not os.path.exists(odir):
                message(f"creating dir {odir}")
                os.makedirs(odir)

            message(f"rendering: {pname} -> {outfilename}...")

            if options.format == "pdf":
                save_pdf(outfilename, diagram)
            elif options.format == "svg":
                save_svg(outfilename, diagram)
            elif options.format == "png":
                save_png(outfilename, diagram)
            else:
                raise RuntimeError(f"Unknown file format: {options.format}")
