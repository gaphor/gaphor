#!/usr/bin/env python
#
# setup.py for Gaphor
#
# vim:sw=4:et
"""Gaphor
"""

MAJOR_VERSION = 0
MINOR_VERSION = 2
MICRO_VERSION = 0

VERSION = '%d.%d.%d' % ( MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION )

GCONF_DOMAIN='/apps/gaphor/' # don't forget trailing slash

import sys, os
from glob import glob
from commands import getoutput, getstatusoutput
from distutils.core import setup, Command
from distutils.command.build_py import build_py
from distutils.command.install import install
from distutils.dep_util import newer

str_version = sys.version[:3]
version = map(int, str_version.split('.'))
if version < [2, 2]:
    raise SystemExit, \
	"Python 2.2 or higher is required, %s found" % str_version


class config_Gaphor(Command):
    description="Configure Gaphor"

    user_options = [
	('pkg-config=', None, 'Path to pkg-config'),
    ]

    pkg_config_checked=False
    config_failed=False

    def initialize_options(self):
	self.pkg_config = 'pkg-config'

    def finalize_options(self):
	# Check for existence of pkg-config
	status, output = getstatusoutput('%s --version' % self.pkg_config)
	if status != 0:
	    print 'pkg-config not found.'
	    raise SystemExit
	print 'Found pkg-config version %s' % output

    def run(self):
	self.pkg_config_check('gobject-2.0', '2.0.0')
	self.pkg_config_check('gtk+-2.0', '2.0.0')
	self.pkg_config_check('pygtk-2.0', '1.99.15')
	self.pkg_config_check('gconf-2.0', '2.0.0')
	self.pkg_config_check('libbonobo-2.0', '2.0.0')
	self.pkg_config_check('libbonoboui-2.0', '2.0.0')
	self.pkg_config_check('diacanvas2', '0.9.1')

	self.module_check('gobject')
	self.module_check('gnome')
	self.module_check('gnome.ui')
	self.module_check('gnome.canvas')
	self.module_check('bonobo')
	self.module_check('bonobo.ui')
	self.module_check('gconf')
	self.module_check('diacanvas')

	if self.config_failed:
	    print 'Config failed.'
	    raise SystemExit

    def pkg_config_check(self, package, version):
	"""Check for availability of a package via pkg-config."""
	retval = os.system('%s --exists %s' % (self.pkg_config, package))
	if retval:
	    print '!!! Required package %s not found.' % package
	    self.config_failed = True
	    return
	pkg_version_str = getoutput('%s --modversion %s' % (self.pkg_config, package))
	pkg_version = map(int, pkg_version_str.split('.'))
	req_version = map(int, version.split('.'))
	if pkg_version >= req_version:
	    print 'Found %s, version %s' % (package, pkg_version_str)
	else:
	    print '!!! Package %s has version %s, should have at least version %s' % ( package, pkg_version_str, version )
	    self.config_failed = True

    def module_check(self, module):
	try:
	    __import__(module)
	except ImportError:
	    print '!!! Required module %s not found.' % module
	    self.config_failed = True
	else:
	    print 'Module %s found' % module


class build_py_Gaphor(build_py):

    description = "build_py and generate gaphor/UML/modelelements.py."

    def run(self):
        build_py.run(self)
        self.generate_modelelements()
        self.generate_version()

    def generate_modelelements(self):
        import utils.genUML
        gen = 'utils/genUML.py'
        xmi = 'doc/UmlMetaModel.xmi'
        outfile = os.path.join(self.build_lib, 'gaphor/UML/modelelements.py')
        self.mkpath(os.path.dirname(outfile))
        if self.force or newer(xmi, outfile) or newer(gen, outfile):
            utils.genUML.generate(xmi, outfile)
        else:
            print 'not generating %s (up-to-date)' % outfile
        self.byte_compile([outfile])

    def generate_version(self):
        outfile = os.path.join(self.build_lib, 'gaphor/version.py')
        self.mkpath(os.path.dirname(outfile))
        f = open(outfile, 'w')
        f.write('VERSION=\'%s\'' % VERSION)
        f.close()
        self.byte_compile([outfile])


class install_config(Command):

    description = "Install a configuration (using GConf)."

    user_options = [
	('install-data=', None, 'installation directory for data files'),
	('force', 'f', 'force installation (overwrite existing keys)')
    ]

    boolean_options = ['force']

    def initialize_options(self):
	self.install_data = None
	self.force = None
	self.gconf_client = None

    def finalize_options(self):
	self.set_undefined_options('install',
				   ('force', 'force'),
				   ('install_data', 'install_data'))

    def run(self):
	import gconf
	self.gconf_client = gconf.client_get_default()
	self._set_value('datadir', self.install_data, 'string')

    def _set_value(self, key, value, type):
	if self.force or not apply(getattr(self.gconf_client, 'get_' + type), (GCONF_DOMAIN + key,)):
            print 'setting gconf value "%s" to "%s"' % (key, value)
	    apply(getattr(self.gconf_client, 'set_' + type), (GCONF_DOMAIN + key, value))

install.sub_commands.append(('install_config', None))

class run_Gaphor(Command):

    description = 'Execute Gaphor from the local directory'

    def run(self):
        print 'Run gaphor'


setup(name='gaphor',
      version=VERSION,
      url='http://gaphor.sourceforge.net',
      author='Arjan J. Molenaar',
      author_email='arjanmol@users.sourceforge.net',
      packages=['gaphor',
		'gaphor.UML',
		'gaphor.diagram',
		'gaphor.ui',
		'gaphor.ui.command',
		'gaphor.misc'
      ],
      data_files=[('gaphor', ['data/gaphor-main-ui.xml',
			      'data/gaphor-diagram-ui.xml',
			      'data/gaphor-editor-ui.xml',
			      'data/gaphor.dtd']),
		  ('gaphor/pixmaps', glob('data/pixmaps/*.png'))
      ],
      scripts=['bin/gaphor'
      ],
      cmdclass={'config': config_Gaphor,
                'build_py': build_py_Gaphor,
                'install_config': install_config,
                'run': run_Gaphor
      }
)

