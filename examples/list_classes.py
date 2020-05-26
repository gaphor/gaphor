#!/usr/bin/python

"""This script lists classes and optionally attributes from UML model created
with Gaphor.
"""

import optparse
import sys

import gaphor.UML as UML
from gaphor.application import Session

# Setup command line options.
usage = "usage: %prog [options] file.gaphor"

parser = optparse.OptionParser(usage=usage)

parser.add_option(
    "-a",
    "--attributes",
    dest="attrs",
    action="store_true",
    help="Print class attributes",
)

(options, args) = parser.parse_args()

if len(args) != 1:
    parser.print_help()
    sys.exit(1)

# The model file to load.
model = args[0]

# Create the Gaphor application object.
session = Session()

# Get services we need.
element_factory = session.get_service("element_factory")
file_manager = session.get_service("file_manager")

# Load model from file.
file_manager.load(model)

# Find all classes using factory select.
for cls in element_factory.select(UML.Class):

    print(f"Found class {cls.name}")

    if options.attrs:

        for attr in cls.ownedAttribute:

            print(f" Attribute: {attr.name}")
