#!/usr/bin/env python3
"""build_pot

Build a PO template (for i18n) and update the .po files to reflect
the last changes.
"""

import glob
import os.path
import sys
import tokenize
from distutils.core import Command

from utils.i18n import pygettext


# from pygettext.main():
class Options:
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
                raise SystemExit(f"Invalid value for --style: {self.style}")
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
            except OSError:
                raise SystemExit(f"Can't read --exclude-file: {self.exclude_file}")
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
        create_pot_file(self.packages, self.output, self.options, verbose=self.verbose)
        merge_files(
            self.all_linguas,
            self.msgmerge,
            self.output,
            self.output_dir,
            verbose=self.verbose,
        )


def create_pot_file(packages, pot_file, options=Options(), verbose=False):
    """
        Create a new .pot file. This is basically a rework of the
    main function of pygettext.
        """
    source_files = []
    for p in packages:
        pathlist = p.split(".")
        path = os.path.join(*pathlist)
        source_files.extend(glob.glob(os.path.join(path, "*.py")))

    # slurp through all the files
    eater = pygettext.TokenEater(options)
    for filename in source_files:
        if verbose:
            print(f"Working on {filename}")
        fp = open(filename, "rb")
        try:
            eater.set_filename(filename)
            try:
                tokens = tokenize.tokenize(fp.readline)
                for _token in tokens:
                    eater(*_token)
            except tokenize.TokenError as e:
                print(f"{e[0]}: {filename}, line {e[1][0]:d}, column {e[1][1]:d}")
        finally:
            fp.close()

    if pot_file == "-":
        fp = sys.stdout
    else:
        fp = open(pot_file, "w")
    try:
        eater.write(fp)
    finally:
        if fp is not sys.stdout:
            fp.close()


def merge_files(all_linguas, msgmerge, pot_file, output_dir, verbose=False):
    if not all_linguas:
        return

    for lingua in all_linguas:
        d = {
            "msgmerge": msgmerge,
            "po": os.path.join(output_dir, lingua + ".po"),
            "pot": pot_file,
        }
        if verbose:
            print(f"Merging {d['pot']} and {d['po']} ")
        res = os.system(f"{d['msgmerge']} {d['po']} {d['pot']} -o {d['po']}")
        if res:
            raise SystemExit("error while running msgmerge.")


if __name__ == "__main__":
    from setuptools import find_packages
    from utils.i18n import LINGUAS

    packages = find_packages(exclude=["utils*", "docs", "tests"])
    output_dir = "po"
    pot_file = os.path.join(output_dir, "gaphor.pot")
    create_pot_file(packages, pot_file, verbose=True)
    merge_files(LINGUAS, "msgmerge", pot_file, output_dir=output_dir, verbose=True)
