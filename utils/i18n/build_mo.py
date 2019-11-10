# vim:sw=4:et
"""build_mo

Generate .mo files from po files.
"""

import os.path
from distutils.core import Command
from distutils.dep_util import newer
from distutils.dir_util import mkpath

from utils.i18n import LINGUAS, msgfmt


class build_mo(Command):
    description = "Create .mo files from .po files"

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [
        ("build-dir=", None, "Directory to build locale files"),
        ("force", "f", "Force creation of .mo files"),
        ("all-linguas", None, ""),
    ]

    boolean_options = ["force"]

    def initialize_options(self):
        self.build_dir = None
        self.force = None
        self.all_linguas = None

    def finalize_options(self):
        self.set_undefined_options("build", ("force", "force"))
        if self.build_dir is None:
            self.set_undefined_options("build", ("build_lib", "build_dir"))
            self.build_dir = os.path.join(self.build_dir, "gaphor", "data", "locale")

        self.all_linguas = self.all_linguas.split(",")

    def run(self):
        """Run msgfmt.make() on all_linguas."""
        po_to_mo(self.all_linguas, self.build_dir)


def po_to_mo(all_linguas, output_dir, force=False):
    if not all_linguas:
        return

    for lingua in all_linguas:
        pofile = os.path.join("po", lingua + ".po")
        outdir = os.path.join(output_dir, lingua, "LC_MESSAGES")
        mkpath(outdir)
        outfile = os.path.join(outdir, "gaphor.mo")
        if force or newer(pofile, outfile):
            print(f"converting {pofile} -> {outfile}")
            msgfmt.make(pofile, outfile)
        else:
            print(f"not converting {pofile} (output up-to-date)")


if __name__ == "__main__":
    output_dir = os.path.join("gaphor", "data", "locale")
    po_to_mo(LINGUAS, output_dir)

else:
    from distutils.command.build import build

    build.sub_commands.append(("build_mo", None))
