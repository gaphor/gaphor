# vim:sw=4:et
"""install_mo

Install gettext packages.

Files will be installed as:
    <install_locales>/<lang>/LC_MESSAGES/<package>.mo
where install_locales should default to:
    <install_base>/share/locale
"""

from distutils.core import Command
#from distutils.util import change_root
import os.path


class install_mo(Command):

    description = 'Install .mo files'

    user_options = [('install-dir=', None,
                     'Directory to install locales into (default: <prefix>/share/locale/<lang>/LC_MESSAGES'),
                    ('all-linguas', None, ''),
    ]

    def initialize_options(self):
        self.install_dir = None
        self.build_dir = None
        self.all_linguas = None

    def finalize_options(self):
        self.set_undefined_options('build_mo',
                                   ('build_dir', 'build_dir'))
        if self.install_dir is None:
            self.set_undefined_options('install',
                                       ('install_base', 'install_dir'))
            self.install_dir = os.path.join(self.install_dir, 'share', 'locale')

        self.name = self.distribution.get_name()
        self.all_linguas = self.all_linguas.split(',')

    def run(self):
        if not self.all_linguas:
            return

        for lang in self.all_linguas:
            mofile = os.path.join(self.build_dir, '%s.mo' % lang)
            path = os.path.join(self.install_dir, lang, 'LC_MESSAGES')
            self.mkpath(path)
            outfile = os.path.join(path, '%s.mo' % self.name)
            self.copy_file(mofile, outfile)

from distutils.command.install import install
install.sub_commands.append(('install_mo', None))
