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
#from distutils.command.install import install
from distutils.dep_util import newer
from utils.build_mo import build, build_mo
from utils.install_mo import install, install_mo
from utils.dist_mo import Distribution

str_version = sys.version[:3]
version = map(int, str_version.split('.'))
if version < [2, 2]:
    raise SystemExit, \
        "Python 2.2 or higher is required, %s found" % str_version


class config_Gaphor(Command):
    description="Configure Gaphor"

    user_options = [
        #('pkg-config=', None, 'Path to pkg-config'),
    ]

    #pkg_config_checked=False
    config_failed=[]

    def initialize_options(self):
        #self.pkg_config = 'pkg-config'
        pass

    def finalize_options(self):
        # Check for existence of pkg-config
        #status, output = getstatusoutput('%s --version' % self.pkg_config)
        #if status != 0:
        #    print 'pkg-config not found.'
        #    raise SystemExit
        #print 'Found pkg-config version %s' % output
        pass

    def run(self):
        #self.pkg_config_check('gobject-2.0', '2.0.0')
        #self.pkg_config_check('gtk+-2.0', '2.0.0')
        #self.pkg_config_check('pygtk-2.0', '1.99.15')
        #self.pkg_config_check('gconf-2.0', '2.0.0')
        #self.pkg_config_check('libbonobo-2.0', '2.0.0')
        #self.pkg_config_check('libbonoboui-2.0', '2.0.0')
        #self.pkg_config_check('diacanvas2', '0.9.1')

        self.module_check('xml.parsers.expat')
        #self.module_check('gobject', 'glib_version', (2, 0))
        self.module_check('gtk', ('gtk_version', (2, 0)),
                                 ('pygtk_version', (1, 99, 16)))
        self.module_check('gnome')
        self.module_check('gnome.ui')
        self.module_check('gnome.canvas')
        self.module_check('bonobo')
        self.module_check('bonobo.ui')
        self.module_check('gconf')
        self.module_check('diacanvas', ('diacanvas_version', (0, 9, 2)))

        print ''
        if self.config_failed:
            print 'Config failed.'
            print 'The following modules can not be found or are to old:'
            print ' ', str(self.config_failed)[1:-1]
            print ''
            raise SystemExit
        else:
            print 'Config succeeded.'
            print 'You can run Gaphor by typing: python setup.py run'

    def pkg_config_check(self, package, version):
        """Check for availability of a package via pkg-config."""
        retval = os.system('%s --exists %s' % (self.pkg_config, package))
        if retval:
            print '!!! Required package %s not found.' % package
            self.config_failed.append(package)
            return
        pkg_version_str = getoutput('%s --modversion %s' % (self.pkg_config, package))
        pkg_version = map(int, pkg_version_str.split('.'))
        req_version = map(int, version.split('.'))
        if pkg_version >= req_version:
            print "Found '%s', version %s." % (package, pkg_version_str)
        else:
            print "!!! Package '%s' has version %s, should have at least version %s." % ( package, pkg_version_str, version )
            self.config_failed.append(package)

    def module_check(self, module, *version_checks):
        """Check for the availability of a module.

        version_checks is a set of ket/version pairs that should be true.
        """
        import string
        try:
            mod = __import__(module)
        except ImportError:
            print "!!! Required module '%s' not found." % module
            self.config_failed.append(module)
        else:
            print "Module '%s' found." % module
            for key, ver in version_checks:
                s_ver = string.join(map(str, ver), '.')
                print "  Checking key '%s.%s' >= %s..." % (module, key, s_ver),
                try:
                    modver = getattr(mod, key)
                except:
                    print "Not found." % key
                    self.config_failed.append(module)
                else:
                    s_modver = string.join(map(str, modver), '.')
                    if modver >= ver:
                        print "Okay (%s)." % s_modver
                    else:
                        print "Failed (%s)" % s_modver
                        self.config_failed.append(module)


class build_py_Gaphor(build_py):

    description = "build_py and generate gaphor/UML/uml2.py."

    def run(self):
        build_py.run(self)
        sys.path.insert(0, self.build_lib)
        self.generate_version()
        self.generate_uml2()

    def generate_uml2(self):
        """Generate gaphor/UML/uml2.py in the build directory."""
        import utils.genUML2
        gen = 'utils/genUML2.py'
        overrides = 'gaphor/UML/uml2.override'
        model = 'doc/UML2.gaphor'
        py_model = 'gaphor/UML/uml2.py'
        outfile = os.path.join(self.build_lib, py_model)
        self.mkpath(os.path.dirname(outfile))
        if self.force or newer(model, outfile) or newer(gen, outfile):
            print 'generating %s from %s...' % (py_model, model)
            utils.genUML2.generate(model, outfile, overrides)
        else:
            print 'not generating %s (up-to-date)' % py_model
        self.byte_compile([outfile])

    def generate_version(self):
        """Create a file gaphor/version.py which contains the current version.
        """
        print 'generating gaphor/version.py'
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

    def finalize_options(self):
        self.set_undefined_options('install',
                                   ('force', 'force'),
                                   ('install_data', 'install_data'))

    def run(self):
        import gconf
        self.gconf_client = gconf.client_get_default()
        self._set_value('datadir', self.install_data, 'string')

    def _set_value(self, key, value, type):
        print "setting gconf value '%s' to '%s'" % (key, value)
        apply(getattr(self.gconf_client, 'set_' + type),
              (GCONF_DOMAIN + key, value))

install.sub_commands.append(('install_config', None))


class run_Gaphor(Command):

    description = 'Launch Gaphor from the local directory'

    user_options = [
        ('build-dir=', None, ''),
        ('command=', 'c', 'execute command'),
        ('file=', 'f', 'execute file'),
    ]

    def initialize_options(self):
        self.build_lib = None
        self.command = None
        self.file = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'))

    def run(self):
        print 'Starting gaphor...'
        self.run_command('build')

        import os.path
        from gaphor import Gaphor
        os.environ['GAPHOR_DATADIR'] = os.path.abspath('data')
        if self.command:
            print 'Executing command: %s...' % self.command
            exec self.command
        elif self.file:
            print 'Starting execution of file: %s...' % self.file
            execfile(self.file, {})
        else:
            Gaphor().main()


setup(name='gaphor',
      version=VERSION,
      description="Gaphor is a UML modeling tool",
      url='http://gaphor.sourceforge.net',
      author='Arjan J. Molenaar',
      author_email='arjanmol@users.sourceforge.net',
      license="GNU General Public License (GPL, see COPYING)",
      long_description="""
      Gaphor is a UML modeling tool written in Python. It uses the GNOME2
      environment for user interaction.""",
      platforms=['GNOME2'],
      all_linguas=['nl'],
      packages=['gaphor',
                'gaphor.UML',
                'gaphor.diagram',
                'gaphor.ui',
                'gaphor.ui.command',
                'gaphor.misc'
      ],
      # data files are relative to <prefix>/share/gaphor (see setup.cfg)
      data_files=[('', ['data/gaphor-main-ui.xml',
                        'data/gaphor-diagram-ui.xml',
                        'data/gaphor-editor-ui.xml',
                        'data/gaphor.dtd']),
                  ('pixmaps', glob('data/pixmaps/*.png'))
      ],
      scripts=['bin/gaphor'],

      distclass=Distribution,
      cmdclass={'config': config_Gaphor,
                'build_py': build_py_Gaphor,
                'install_config': install_config,
                'build': build,
                'build_mo': build_mo,
                'install': install,
                'install_mo': install_mo,
                'run': run_Gaphor
      }
)

