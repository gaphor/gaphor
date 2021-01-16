"""Import hook for PyGObject https://wiki.gnome.org/PyGObject."""

from PyInstaller.utils.hooks import get_gi_typelibs

binaries, datas, hiddenimports = get_gi_typelibs("GtkosxApplication", "1.0")
