import os
import pathlib
import sys

PYVER = "3.7"

resources = os.environ["RESOURCEPATH"]
cache = pathlib.Path.home() / ".cache" / "gaphor"
if not cache.exists():
    cache.mkdir()

print(f"App contents folder is {resources}, cache is {cache}")


while sys.path[0] == resources:
    del sys.path[0]


os.environ["FONTCONFIG_SYSROOT"] = f"{resources}"
os.environ["GTK_DATA_PREFIX"] = f"{resources}"
os.environ["GI_TYPELIB_PATH"] = f"{resources}/lib/girepository-1.0"

os.environ["GTK_EXE_PREFIX"] = f"{resources}"
os.environ["GTK_PATH"] = f"{resources}"
os.environ["XDG_DATA_HOME"] = f"{resources}/share"
os.environ["XDG_DATA_DIRS"] = f"{resources}/share"
os.environ["FONTCONFIG_FILE"] = f"{resources}/etc/fonts/fonts.conf"
os.environ["GI_TYPELIB_PATH"] = f"{resources}/lib/girepository-1.0"
os.environ["GDK_PIXBUF_MODULEDIR"] = f"{resources}/lib/gdk-pixbuf-2.0/2.10.0/loaders"

os.environ["GDK_PIXBUF_MODULE_FILE"] = f"{cache}/gdk-pixbuf-2.0-loaders.cache"
os.environ["GTK_IM_MODULE_FILE"] = f"{cache}/immodules.cache"

os.system(f'"{resources}/../MacOS/gdk-pixbuf-query-loaders" --update-cache')
os.system(f'"{resources}/../MacOS/gtk-query-immodules-3.0" --update-cache')


from gaphor.ui import main  # noqa: E402

main(sys.argv)
