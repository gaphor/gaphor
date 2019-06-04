#!/usr/bin/python

import gaphor
from gaphor.storage import storage
import gaphor.UML as UML

from gaphas.painter import ItemPainter
from gaphas.view import View

import cairo

import optparse
import os
import re
import sys


def pkg2dir(package):
    """
    Return directory path from UML package class.
    """
    name = []
    while package:
        name.insert(0, package.name)
        package = package.package
    return "/".join(name)


def message(msg):
    """
    Print message if user set verbose mode.
    """
    global options
    if options.verbose:
        print(msg, file=sys.stderr)


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
    help="process diagrams which name matches given regular expresion;"
    " name includes package name; regular expressions are case insensitive",
)

(options, args) = parser.parse_args()

if not args:
    parser.print_help()
    # sys.exit(1)

model = UML.ElementFactory()


name_re = None
if options.regex:
    name_re = re.compile(options.regex, re.I)

# we should have some gaphor files to be processed at this point
for model in args:
    message("loading model %s" % model)
    storage.load(model, model)
    message("\nready for rendering\n")

    for diagram in model.select(lambda e: e.isKindOf(UML.Diagram)):
        odir = pkg2dir(diagram.package)

        # just diagram name
        dname = diagram.name
        # full diagram name including package path
        pname = "%s/%s" % (odir, dname)

        if options.underscores:
            odir = odir.replace(" ", "_")
            dname = dname.replace(" ", "_")

        if name_re and not name_re.search(pname):
            message("skipping %s" % pname)
            continue

        if options.dir:
            odir = "%s/%s" % (options.dir, odir)

        outfilename = "%s/%s.%s" % (odir, dname, options.format)

        if not os.path.exists(odir):
            message("creating dir %s" % odir)
            os.makedirs(odir)

        message("rendering: %s -> %s..." % (pname, outfilename))

        view = View(diagram.canvas)
        view.painter = ItemPainter()

        tmpsurface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 0, 0)
        tmpcr = cairo.Context(tmpsurface)
        view.update_bounding_box(tmpcr)
        tmpcr.show_page()
        tmpsurface.flush()

        w, h = view.bounding_box.width, view.bounding_box.height
        if options.format == "pdf":
            surface = cairo.PDFSurface(outfilename, w, h)
        elif options.format == "svg":
            surface = cairo.SVGSurface(outfilename, w, h)
        elif options.format == "png":
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w + 1), int(h + 1))
        else:
            assert False, "unknown format %s" % options.format
        cr = cairo.Context(surface)
        view.matrix.translate(-view.bounding_box.x, -view.bounding_box.y)
        view.paint(cr)
        cr.show_page()

        if options.format == "png":
            surface.write_to_png(outfilename)

        surface.flush()
        surface.finish()


def main():
    pass
