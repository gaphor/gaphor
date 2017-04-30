"""
Command for running gaphor and tests directly from setup.py.
"""

from __future__ import absolute_import
from __future__ import print_function
import sys, os.path
from distutils.core import Command
from pkg_resources import load_entry_point

class run(Command):

    description = 'Launch Gaphor from the local directory'

    user_options = [
        ('build-dir=', None, ''),
        ('command=', 'c', 'execute command'),
        ('file=', 'f', 'execute file'),
        ('doctest=', 'd', 'execute doctests in module (e.g. gaphor.geometry)'),
        ('unittest=', 'u', 'execute unittest file (e.g. tests/test-ns.py)'),
        ('model=', 'm', 'load a model file'),
        ('coverage', None, 'Calculate coverage (requires coverage.py)'),
        ('profile', 'p', 'Run with profiling enabled'),
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
        self.profile = None

    def finalize_options(self):
        self.set_undefined_options('build',
                                   ('build_lib', 'build_lib'))

    def run(self):
        print('Starting Gaphor...')

        if self.model:
            print('Starting with model file', self.model)

        for cmd_name in self.get_sub_commands():
            self.run_command(cmd_name)
        #if self.build_lib not in sys.path:
            #sys.path.insert(0, self.build_lib)
        
        import gaphor
        #os.environ['GAPHOR_DATADIR'] = os.path.abspath('data')
        if self.coverage:
            import coverage
            coverage.start()

        if self.command:
            print('Executing command: %s...' % self.command)
            exec(self.command)

        elif self.doctest:
            print('Running doctest cases in module: %s...' % self.doctest)
            import imp
            # use zope's one since it handles coverage right
            from zope.testing import doctest

            # Figure out the file:
            f = os.path.join(*self.doctest.split('.')) + '.py'
            fp = open(f)
            # Prepend module's package path to sys.path
            pkg = os.path.join(self.build_lib, *self.doctest.split('.')[:-1])
            #if pkg:
            #    sys.path.insert(0, pkg)
            #    print 'Added', pkg, 'to sys.path'
            # Load the module as local module (without package)
            test_module = imp.load_source(self.doctest.split('.')[-1], f, fp)
            failure, tests = doctest.testmod(test_module, name=self.doctest,
                 optionflags=doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE)
            if self.coverage:
                print()
                print('Coverage report:')
                coverage.report(f)
            sys.exit(failure != 0)

        elif self.unittest:
            # Running a unit test is done by opening the unit test file
            # as a module and running the tests within that module.
            print('Running test cases in unittest file: %s...' % self.unittest)
            import imp, unittest
            fp = open(self.unittest)
            test_module = imp.load_source('gaphor_test', self.unittest, fp)
            test_suite = unittest.TestLoader().loadTestsFromModule(test_module)
            #test_suite = unittest.TestLoader().loadTestsFromName(self.unittest)
            test_runner = unittest.TextTestRunner(verbosity=self.verbosity)
            result = test_runner.run(test_suite)
            if self.coverage:
                print()
                print('Coverage report:')
                coverage.report(self.unittest)
            sys.exit(not result.wasSuccessful())

        elif self.file:
            print('Executing file: %s...' % self.file)
            dir, f = os.path.split(self.file)
            print('Extending PYTHONPATH with %s' % dir)
            #sys.path.append(dir)
            exec(compile(open(self.file).read(), self.file, 'exec'), {})
        else:
            print('Launching Gaphor...')
            del sys.argv[1:]
            starter = load_entry_point('gaphor==%s' % (self.distribution.get_version(),), 'console_scripts', 'gaphor')

            if self.profile:
                print('Enabling profiling...')
                try:
                    import cProfile
                    import pstats
                    prof = cProfile.Profile()
                    prof.runcall(starter)
                    prof.dump_stats('gaphor.prof')
                    p = pstats.Stats('gaphor.prof')
                    p.strip_dirs().sort_stats('time').print_stats(20)
                except ImportError as ex:
                    import hotshot, hotshot.stats
                    prof = hotshot.Profile('gaphor.prof')
                    prof.runcall(starter)
                    prof.close()
                    stats = hotshot.stats.load('gaphor.prof')
                    stats.strip_dirs()
                    stats.sort_stats('time', 'calls')
                    stats.print_stats(20)
            else:
                starter()

    sub_commands = [('build', None)]

# vim:sw=4:et
