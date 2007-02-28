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
from distutils.command.build_py import build_py
from distutils.command.install_lib import install_lib
from distutils.dep_util import newer
from distutils.util import byte_compile
from distutils.dir_util import mkpath
from utils.build_mo import build, build_mo
from utils.build_pot import build_pot
from utils.install_mo import install, install_mo

str_version = sys.version[:3]
version = map(int, str_version.split('.'))
if version < [2, 4]:
    raise SystemExit, \
        "Python 2.4 or higher is required, %s found" % str_version


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

#class build_Gaphor(build):
#
#    def run(self):
#        self.run_command('config')
#        build.run(self)
#

def generate_version(dir, data_dir):
    """
    Create a file gaphor/version.py which contains the current version.
    """
    outfile = os.path.join(dir, 'gaphor', 'version.py')
    print 'generating %s' % outfile, dir, data_dir
    mkpath(os.path.dirname(outfile))
    f = open(outfile, 'w')
    f.write('"""\nVersion information generated by setup.py. DO NOT EDIT.\n"""\n\n')
    f.write('VERSION=\'%s\'\n' % VERSION)
    # expand backspaces
    f.write('DATA_DIR=\'%s\'\n' % data_dir.replace('\\', '\\\\'))
    if os.name == 'nt':
        home = 'USERPROFILE'
    else:
        home = 'HOME'
    f.write('import os\n')
    f.write('USER_DATA_DIR=os.path.join(os.getenv(\'%s\'), \'.gaphor\')\n' % home)
    f.write('del os\n')
    f.close()
    byte_compile([outfile])


class build_version(Command):

    user_options = [
        ('build-lib=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ('data-dir', None, "data directory (where images and plugins reside)"),
        ]
    boolean_options = [ 'force' ]

    def initialize_options(self):
        self.build_lib = None
        self.force = 0
        self.data_dir = None

    def finalize_options(self):
            self.set_undefined_options('build',
                                       ('build_purelib', 'build_lib'),
                                       ('force', 'force'))
            self.data_dir = os.path.join(os.getcwd(), 'data')

    def run(self):
        generate_version(self.build_lib, self.data_dir)

build.sub_commands.insert(0, ('build_version', None))

class build_uml(Command):

    description = "Generate gaphor/UML/uml2.py."

    user_options = [
        ('build-lib=','b', "build directory (where to install from)"),
        ('force', 'f', "force installation (overwrite existing files)"),
        ]

    boolean_options = [ 'force' ]

    def initialize_options(self):
        self.build_lib = None
        self.force = 0
        self.data_dir = None

    def finalize_options(self):
            self.set_undefined_options('build',
                                       ('build_lib', 'build_lib'),
                                       ('force', 'force'))

    def run(self):
        sys.path.insert(0, self.build_lib)
        self.generate_uml2()

    def generate_uml2(self):
        """
        Generate gaphor/UML/uml2.py in the build directory.
        """
        import utils.genUML2
        gen = os.path.join('utils', 'genUML2.py')
        overrides = os.path.join('gaphor', 'UML', 'uml2.override')
        model = os.path.join('gaphor', 'UML', 'uml2.gaphor')
        py_model = os.path.join('gaphor', 'UML', 'uml2.py')
        outfile = os.path.join(self.build_lib, py_model)
        self.mkpath(os.path.dirname(outfile))
        if self.force or newer(model, outfile) \
                      or newer(overrides, outfile) \
                      or newer(gen, outfile):
            print 'generating %s from %s...' % (py_model, model)
            print '  (warnings can be ignored)'
            utils.genUML2.generate(model, outfile, overrides)
        else:
            print 'not generating %s (up-to-date)' % py_model
        byte_compile([outfile])

build.sub_commands.append(('build_uml', None))


class install_version(Command):

    user_options = [
        ('install-dir=', 'd', "directory to install to"),
        ('install-data=', 'd', "directory where data files are installed"),
        ]


    def initialize_options(self):
        install_lib.initialize_options(self)
        self.install_dir= None
        self.install_data= None

    def finalize_options(self):
        install_lib.finalize_options(self)
        self.set_undefined_options('install_lib',
                                   ('install_dir', 'install_dir'))
        self.set_undefined_options('install_data',
                                   ('install_data', 'install_dir'))

    def run(self):
        # install a new version.py with install_data as data_dir;
        # get rid of install root directory
        print 'self', dir(self)
        print 'self.get_finalized_command("install")', dir(self.get_finalized_command('install'))
        
        skip = len(self.get_finalized_command('install').root or '')

        generate_version(self.install_dir, self.install_data[skip:])


class run_Gaphor(Command):

    description = 'Launch Gaphor from the local directory'

    user_options = [
        ('build-dir=', None, ''),
        ('command=', 'c', 'execute command'),
        ('file=', 'f', 'execute file'),
        ('doctest=', 'd', 'execute doctests in module (e.g. gaphor.geometry)'),
        ('unittest=', 'u', 'execute unittest file (e.g. tests/test-ns.py)'),
        ('model=', 'm', 'load a model file'),
        ('coverage', None, 'Calculate coverage (utils/coverage.py)'),
    ]

    def initialize_options(self):
        self.build_lib = None
        self.command = None
        self.file = None
        self.doctest = None
        self.unittest = None
        self.model = None
        self.coverage = None
        self.verbosity = 2

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'))

    def run(self):
        print 'Starting Gaphor...'
        print 'Starting with model file', self.model
        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)

        import os.path
        import gaphor
        #os.environ['GAPHOR_DATADIR'] = os.path.abspath('data')
        if self.coverage:
            from utils import coverage
            coverage.start()

        if self.command:
            print 'Executing command: %s...' % self.command
            exec self.command

        elif self.doctest:
            print 'Running doctest cases in module: %s...' % self.doctest
            import imp
            # use zope's one since it handles coverage right
            from zope.testing import doctest

            # Figure out the file:
            f = os.path.join(*self.doctest.split('.')) + '.py'
            fp = open(f)
            # Prepend module's package path to sys.path
            pkg = os.path.join(self.build_lib, *self.doctest.split('.')[:-1])
            if pkg:
                sys.path.insert(0, pkg)
                print 'Added', pkg, 'to sys.path'
            # Load the module as local module (without package)
            test_module = imp.load_source(self.doctest.split('.')[-1], f, fp)
            failure, tests = doctest.testmod(test_module, name=self.doctest,
                 optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
            if self.coverage:
                print
                print 'Coverage report:'
                coverage.report(f)
            sys.exit(failure != 0)

        elif self.unittest:
            # Running a unit test is done by opening the unit test file
            # as a module and running the tests within that module.
            print 'Running test cases in unittest file: %s...' % self.unittest
            import imp, unittest
            fp = open(self.unittest)
            test_module = imp.load_source('gaphor_test', self.unittest, fp)
            test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
            #test_suite = unittest.TestLoader().loadTestsFromName(self.unittest)
            test_runner = unittest.TextTestRunner(verbosity=self.verbosity)
            result = test_runner.run(test_suite)
            if self.coverage:
                print
                print 'Coverage report:'
                coverage.report(self.unittest)
            sys.exit(not result.wasSuccessful())

        elif self.file:
            print 'Executing file: %s...' % self.file
            dir, f = os.path.split(self.file)
            print 'Extending PYTHONPATH with %s' % dir
            sys.path.append(dir)
            execfile(self.file, {})
        else:
            print 'Launching Gaphor...'
            gaphor.main(self.model)

    sub_commands = [('build', None)]


class tests_Gaphor(Command):

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

      cmdclass={'config': config_Gaphor,
                'build_uml': build_uml,
                'build_version': build_version,
                'build_mo': build_mo,
                'build_pot': build_pot,
                'install_mo': install_mo,
                'run': run_Gaphor,
                'tests': tests_Gaphor
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
