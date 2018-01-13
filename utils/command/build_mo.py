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
"""build_mo

Generate .mo files from po files.
"""

from __future__ import absolute_import
from __future__ import print_function

import os.path
from distutils.core import Command
from distutils.dep_util import newer

from . import msgfmt


class build_mo(Command):
    description = 'Create .mo files from .po files'

    # List of option tuples: long name, short name (None if no short
    # name), and help string.
    user_options = [('build-dir=', None,
                     'Directory to build locale files'),
                    ('force', 'f', 'Force creation of .mo files'),
                    ('all-linguas', None, ''),
                    ]

    boolean_options = ['force']

    def initialize_options(self):
        self.build_dir = None
        self.force = None
        self.all_linguas = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('force', 'force'))
        if self.build_dir is None:
            self.set_undefined_options('build',
                                       ('build_lib', 'build_dir'))
            self.build_dir = os.path.join(self.build_dir, 'gaphor', 'data', 'locale')

        self.all_linguas = self.all_linguas.split(',')

    def run(self):
        """Run msgfmt.make() on all_linguas."""
        if not self.all_linguas:
            return

        for lingua in self.all_linguas:
            pofile = os.path.join('po', lingua + '.po')
            outdir = os.path.join(self.build_dir, lingua, 'LC_MESSAGES')
            self.mkpath(outdir)
            outfile = os.path.join(outdir, 'gaphor.mo')
            if self.force or newer(pofile, outfile):
                print('converting %s -> %s' % (pofile, outfile))
                msgfmt.make(pofile, outfile)
            else:
                print('not converting %s (output up-to-date)' % pofile)


from distutils.command.build import build

build.sub_commands.append(('build_mo', None))
