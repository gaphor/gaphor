
EXTRA_DIST = __init__.py namespace.py

CLEANFILES = *.pyc *.pyo

INCLUDES = $(GTK_CFLAGS) $(PYTHON_INCLUDES) $(PYGTK_CFLAGS)
LDADD = $(GTK_LIBS)

treemodeldir = $(pythondir)
treemodelexecdir = $(pyexecdir)

treemodelexec_LTLIBRARIES = treemodelmodule.la
treemodelmodule_la_LDFLAGS = -module -avoid-version -export-symbols-regex inittreemodel
treemodelmodule_la_LIBADD = $(DIACANVAS_LIBS)
treemodelmodule_la_SOURCES = treemodel.c treemodelmodule.c
nodist_treemodelmodule_la_SOURCES = pytreemodel.c

pytreemodel.c: pytreemodel.defs pytreemodel.override

all-local:
	test -f $(srcdir)/treemodelmodule.so || $(LN_S) $(srcdir)/.libs/treemodelmodule.so $(srcdir)
	(cd .. && $(PYTHON) -c "import tree.treemodel")

.defs.c:
	(cd $(srcdir) \
	 && $(PYGTK_CODEGEN) \
	    --register $(PYGTK_DEFSDIR)/pango-types.defs \
	    --register $(PYGTK_DEFSDIR)/gdk-types.defs \
	    --register $(PYGTK_DEFSDIR)/gtk-types.defs \
	    --override $*.override \
	    --prefix $* $*.defs) > gen-$*.c \
	 && cp gen-$*.c $*.c \
	 && rm -f gen-$*.c

