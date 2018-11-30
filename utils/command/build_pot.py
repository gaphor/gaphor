#!/usr/bin/env python

# Copyright (C) 2003-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License
# more details.
#
# You should have received a copy of the GNU Library General Public
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""build_pot

Build a PO template (for i18n) and update the .po files to reflect
the last changes.
"""
from __future__ import print_function

from builtins import object
import os.path
import sys
from distutils.core import Command

from utils.command import pygettext


# from pygettext.main():
class Options(object):
    # constants
    GNU = 1
    SOLARIS = 2
    # defaults
    extractall = 0  # FIXME: currently this option has no effect at all.
    keywords = []
    writelocations = 1
    locationstyle = GNU
    verbose = 0
    width = 78
    excludefilename = ""
    docstrings = 0
    nodocstrings = {}
    toexclude = []


class build_pot(Command):
    description = "Generate a .po template file (.pot) from python source files"

    user_options = [
        ("msgmerge=", None, "location of the msgmerge program"),
        ("extract-all", "a", ""),
        ("default-domain=", "d", ""),
        ("escape", "E", ""),
        ("docstrings", "D", ""),
        ("keyword=", "k", "Comma separated list of keywords"),
        ("no-default-keywords", "K", ""),
        ("add-location", "n", ""),
        ("no-location", None, ""),
        ("style=", "S", 'POT file style "gnu" or "solaris"'),
        ("output=", "o", ""),
        ("output-dir=", "p", ""),
        ("width=", "w", ""),
        ("exclude-file=", "x", ""),
        ("all-linguas=", None, ""),
        # ('no-docstrings=', 'X', ''),
    ]

    boolean_options = [
        "extract-all",
        "escape",
        "docstrings",
        "no-default-keywords",
        "add-location",
        "no-location",
        "no-docstrings",
    ]

    # constants
    GNU = 1
    SOLARIS = 2

    def initialize_options(self):
        self.podir = "po"
        self.msgmerge = "msgmerge"

        self.options = Options()

        # defaults for variable parsing:
        self.escape = 0
        self.width = 78
        self.extract_all = 0  # doesn't do anything yet
        self.default_domain = None
        self.keyword = None
        self.no_default_keywords = 0
        self.no_location = 0
        self.style = None
        self.output = None
        self.output_dir = None
        self.docstrings = 0
        self.exclude_file = None
        # self.no_docstrings = None
        self.all_linguas = []

    def finalize_options(self):
        options = self.options

        self.name = self.distribution.get_name()

        # Build default options for the TokenEater
        if self.default_domain:
            self.output = self.default_domain + ".pot"
        if self.keyword:
            options.keywords.extend(self.keyword.split(","))
        if self.no_default_keywords:
            options.keywords = []
        if self.no_location:
            options.writelocations = 0
        if self.style:
            if self.style == "gnu":
                options.locationstyle = self.GNU
            elif self.style == "solaris":
                options.locationstyle = self.SOLARIS
            else:
                raise SystemExit("Invalid value for --style: %s" % self.style)
        if not self.output:
            self.output = self.distribution.get_name() + ".pot"
        if not self.output_dir:
            self.output_dir = self.podir
        if self.docstrings:
            options.docstrings = 1
        options.width = int(self.width)
        if self.exclude_file:
            try:
                fp = open(self.exclude_file)
                options.toexclude = fp.readlines()
                fp.close()
            except IOError:
                raise SystemExit("Can't read --exclude-file: %s" % self.exclude_file)
        # skip: self.no_docstrings
        if self.all_linguas:
            self.all_linguas = self.all_linguas.split(",")

        # calculate escapes
        pygettext.make_escapes(self.escape)

        # calculate all keywords
        options.keywords.append("_")

        if self.output_dir:
            self.output = os.path.join(self.output_dir, self.output)

        self.packages = self.distribution.packages

        # self.all_linguas = self.distribution.get_all_linguas()
        # self.all_linguas = self.distribution.options['po']['all_linguas']

    def run(self):
        self.create_pot_file()
        self.merge_files()

    def create_pot_file(self):
        """
            Create a new .pot file. This is basically a rework of the
        main function of pygettext.
            """
        import glob
        import tokenize

        source_files = []
        for p in self.packages:
            pathlist = p.split(".")
            path = os.path.join(*pathlist)
            source_files.extend(glob.glob(os.path.join(path, "*.py")))

        # slurp through all the files
        eater = pygettext.TokenEater(self.options)
        for filename in source_files:
            if self.verbose:
                print("Working on %s" % filename)
            fp = open(filename)
            try:
                eater.set_filename(filename)
                try:
                    tokenize.tokenize(fp.readline, eater)
                except tokenize.TokenError as e:
                    print(
                        "%s: %s, line %d, column %d"
                        % (e[0], filename, e[1][0], e[1][1])
                    )
            finally:
                fp.close()

        # write the output
        if self.output == "-":
            fp = sys.stdout
        else:
            fp = open(self.output, "w")
        try:
            eater.write(fp)
        finally:
            if fp is not sys.stdout:
                fp.close()

    def merge_files(self):
        if not self.all_linguas:
            return

        for lingua in self.all_linguas:
            d = {
                "msgmerge": self.msgmerge,
                "po": os.path.join(self.output_dir, lingua + ".po"),
                "pot": self.output,
            }
            if self.verbose:
                sys.stdout.write("Merging %(pot)s and %(po)s " % d)
                sys.stdout.flush()
            res = os.system("%(msgmerge)s %(po)s %(pot)s -o %(po)s" % d)
            if res:
                SystemExit, "error while running msgmerge."
