# vim:sw=4:et
"""build_mo

Generate .mo files from po files.
"""

from distutils.core import Command
from distutils.dep_util import newer
from distutils.command.build import build as _build
import os.path
import msgfmt

class build(_build):
    description = "New build class, which adds the property to add locales."

    def initialize_options(self):
        _build.initialize_options(self)
        self.build_locales = None

    def finalize_options(self):
        _build.finalize_options(self)
        if not self.build_locales:
            self.build_locales = os.path.join(self.build_base, 'locale')

build.sub_commands.append(('build_mo', None))

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

    def initialize_options (self):
        self.build_dir = None
        self.force = None
        self.all_linguas = None

    def finalize_options (self):
        self.set_undefined_options('build',
                                   ('build_locales', 'build_dir'),
                                   ('force', 'force'))
        self.all_linguas = self.all_linguas.split(',')

    def run (self):
	"""Run msgfmt.make() on all_linguas."""
	if not self.all_linguas:
	    return

	self.mkpath(self.build_dir)
	for lingua in self.all_linguas:
	    pofile = os.path.join('po', lingua + '.po')
	    outfile = os.path.join(self.build_dir, lingua + '.mo')
	    if self.force or newer(pofile, outfile):
                print 'converting %s -> %s' % (pofile, outfile)
		msgfmt.make(pofile, outfile)
            else:
                print 'not converting %s (output up-to-date)' % pofile

