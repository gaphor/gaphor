#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
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
"""
This file provides the code generator which transforms gaphor/UML/uml2.gaphor
into gaphor/UML/uml2.py.

Also a distutils tool, build_uml, is provided.
"""

import os.path
from distutils.core import Command
from distutils.util import byte_compile
from distutils.dep_util import newer


class build_uml(Command):

    description = "Generate gaphor/UML/uml2.py."

    user_options = [
        ('build-lib=', 'b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ]

    boolean_options = [ 'force' ]

    def initialize_options(self):
        #self.build_lib = None
        self.force = 0
        self.data_dir = None

    def finalize_options(self):
            self.set_undefined_options('build',
                                       #('build_lib', 'build_lib'),
                                       ('force', 'force'))

    def run(self):
        import sys
        #sys.path.insert(0, self.build_lib)
        self.generate_uml2()

    def generate_uml2(self):
        """
        Generate gaphor/UML/uml2.py in the build directory.
        """
        gen = os.path.join('utils', 'command', 'gen_uml.py')
        overrides = os.path.join('gaphor', 'UML', 'uml2.override')
        model = os.path.join('gaphor', 'UML', 'uml2.gaphor')
        py_model = os.path.join('gaphor', 'UML', 'uml2.py')
        outfile = py_model #os.path.join(self.build_lib, py_model)
        self.mkpath(os.path.dirname(outfile))
        if self.force or newer(model, outfile) \
                      or newer(overrides, outfile) \
                      or newer(gen, outfile):
            print 'generating %s from %s...' % (py_model, model)
            print '  (warnings can be ignored)'
            import gen_uml
            gen_uml.generate(model, outfile, overrides)
        else:
            print 'not generating %s (up-to-date)' % py_model
        byte_compile([outfile])


# vim:sw=4:et
