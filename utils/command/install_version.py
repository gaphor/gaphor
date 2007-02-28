
from distutils.core import Command
from distutils.command.install import install
from build_version import generate_version


class install_version(Command):

    user_options = [
        ('install-dir=', 'd', "directory to install to"),
        ('install-data=', 'd', "directory where data files are installed"),
        ]


    def initialize_options(self):
        self.install_dir= None
        self.install_data= None

    def finalize_options(self):
        self.set_undefined_options('install_lib',
                                   ('install_dir', 'install_dir'))
        self.set_undefined_options('install',
                                   ('install_data', 'install_data'))

    def run(self):
        # install a new version.py with install_data as data_dir;
        # get rid of install root directory
        
        skip = len(self.get_finalized_command('install').root or '')

        generate_version(self.install_dir, self.install_data[skip:],
           self.distribution.get_version())

install.sub_commands.append(("install_version", None))

#vim:sw=4:et

