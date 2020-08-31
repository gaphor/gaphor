"""Temporary hook to support HarfBuzz

Work around for https://github.com/pyinstaller/pyinstaller/issues/5129
Both this file and the pre_safe import hook are required.

"""

from PyInstaller.utils.hooks import get_gi_typelibs

binaries, datas, hiddenimports = get_gi_typelibs('HarfBuzz', '0.0')

