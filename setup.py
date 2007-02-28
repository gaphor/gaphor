#!/usr/bin/env python
#
# setup.py for Gaphor
#
"""
Gaphor
"""

MAJOR_VERSION = 0
MINOR_VERSION = 9
MICRO_VERSION = 1

VERSION = '%d.%d.%d' % ( MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION )

LINGUAS = [ 'ca', 'es', 'nl', 'sv' ]

TESTS = [
    'gaphor.actions.tests.test_itemactions',
    'gaphor.actions.tests.test_placementactions',
    'gaphor.adapters.tests.test_connector',
    'gaphor.adapters.tests.test_editor',
    'gaphor.diagram.tests.test_diagramitem',
    'gaphor.diagram.tests.test_class',
    'gaphor.diagram.tests.test_action',
    'gaphor.diagram.tests.test_handletool',
    'gaphor.diagram.tests.test_interfaces',
    'gaphor.diagram.tests.test_style',
    'gaphor.ui.tests.test_diagramtab',
    'gaphor.ui.tests.test_mainwindow',
    'gaphor.UML.tests.test_elementfactory',
    ]

#GCONF_DOMAIN='/apps/gaphor/' # don't forget trailing slash

import sys, os
from glob import glob
from commands import getoutput, getstatus, getstatusoutput

# Py2App should be imported before the utils classes are loaded
try:
    import py2app
except ImportError:
    print "No py2app, can't create application bundle"
else:
    from modulegraph.modulegraph import AddPackagePath
    AddPackagePath('gaphor', 'build/lib/gaphor')
    AddPackagePath('gaphor.UML', 'build/lib/gaphor/UML')


from distutils.core import setup, Command
from distutils.command.build import build
from distutils.command.install import install
from distutils.command.build_py import build_py
from distutils.command.install_lib import install_lib
from distutils.dep_util import newer
from distutils.util import byte_compile
from distutils.dir_util import mkpath
from utils.command.build_mo import build_mo
from utils.command.build_pot import build_pot
from utils.command.install_mo import install_mo
from utils.command.build_uml import build_uml
from utils.command.build_version import build_version
from utils.command.install_version import install_version
from utils.command.run import run

str_version = sys.version[:3]
version = map(int, str_version.split('.'))
if version < [2, 4]:
    raise SystemExit, \
        "Python 2.4 or higher is required, %s found" % str_version


class config(Command):
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
        self.module_check('pygtk')
        import pygtk
        pygtk.require('2.0')

        self.module_check('xml.parsers.expat')
        self.module_check('gtk', ('gtk_version', (2, 8)),
                                 ('pygtk_version', (2, 8)))

        print ''
        if self.config_failed:
            print 'Config failed.'
            print 'The following modules can not be found or are to old:'
            print ' ', str(self.config_failed)[1:-1]
            print ''
            raise SystemExit
        else:
            print 'Config succeeded.'

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


build.sub_commands.insert(0, ('config', None))


class tests(Command):

    description = 'Run the Gaphor test suite.'

    user_options = [
    ]

    def initialize_options(self):
        self.verbosity = 9

    def finalize_options(self):
        pass

    def run(self):
        print 'Starting Gaphor test-suite...'

        self.run_command('build')

        import unittest

        test_suite = unittest.defaultTestLoader.loadTestsFromNames(TESTS)

        test_runner = unittest.TextTestRunner(verbosity=self.verbosity)
        result = test_runner.run(test_suite)
        sys.exit(not result.wasSuccessful())

def plugin_data(name):
    return 'plugins/%s' % name, glob('data/plugins/%s/*.*' % name)


setup(name='gaphor',
      version=VERSION,
      description="Gaphor is a UML modeling tool",
      url='http://gaphor.sourceforge.net',
      author='Arjan J. Molenaar',
      author_email='arjanmol@users.sourceforge.net',
      license="GNU General Public License (GPL, see COPYING)",
      long_description="Gaphor is a UML modeling tool written in Python. "
      "It uses the GNOME2 environment for user interaction.",
      platforms=['GNOME2'],
      packages=['gaphor',
                'gaphor.UML',
                'gaphor.UML.tests',
                'gaphor.diagram',
                'gaphor.diagram.tests',
                'gaphor.ui',
                'gaphor.ui.tests',
                'gaphor.misc',
                'gaphor.adapters',
                'gaphor.adapters.tests',
                'gaphor.actions',
                'gaphor.actions.tests',
                'gaphas',
                'zope',
                'zope.interface',
                'zope.component.bbb',
                'zope.component.bbb.tests',
                'zope.interface.common',
                'zope.component',
                'zope.exceptions',
                'zope.deprecation',
                'zope.testing',
                
      ],
#      ext_modules=ext_modules,
      # data files are relative to <prefix>/share/gaphor (see setup.cfg)
      data_files=[('', ['data/icons.xml']),
                  ('pixmaps', glob('data/pixmaps/*.png')),
                  plugin_data('plugineditor'),
                  plugin_data('alignment'),
                  plugin_data('checkmetamodel'),
                  plugin_data('diagramlayout'),
                  plugin_data('liveobjectbrowser'),
                  plugin_data('pngexport'),
                  plugin_data('pynsource'),
                  plugin_data('svgexport'),
                  plugin_data('pdfexport'),
                  plugin_data('xmiexport')
      ],
      scripts=['bin/gaphor', 'bin/gaphorconvert'],

      cmdclass={'config': config,
                'build_uml': build_uml,
                'build_version': build_version,
                'install_version': install_version,
                'build_mo': build_mo,
                'build_pot': build_pot,
                'install_mo': install_mo,
                'run': run,
                'tests': tests
      },
#      app=['gaphor-osx.py'],
      options = dict(
         py2app = dict(
             includes=['atk', 'pango', 'cairo', 'pangocairo'],
#             CFBundleDisplayName='Gaphor',
#             CFBundleIdentifier='net.sourceforge.gaphor'
         ),
         build_pot = dict(
             all_linguas = ','.join(LINGUAS),
         ),
         build_mo = dict(
             all_linguas = ','.join(LINGUAS),
         ),
         install_mo = dict(
             all_linguas = ','.join(LINGUAS),
         ),
     )
)

# vim:sw=4:et
