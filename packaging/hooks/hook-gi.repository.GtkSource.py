"""Import hook for PyGObject https://wiki.gnome.org/PyGObject."""

from PyInstaller.utils.hooks.gi import collect_glib_share_files, get_gi_typelibs

binaries, datas, hiddenimports = get_gi_typelibs("GtkSource", "4")

datas += collect_glib_share_files("gtksourceview-4")
