AUTOMAKE_OPTIONS = 1.5

INCLUDES = $(DIACANVAS2_CFLAGS) $(PYTHON_INCLUDES) $(PYGTK_CFLAGS)
LDADD = $(DIACANVAS2_LIBS)

PYGTK_DEFSDIR = @PYGTK_DEFSDIR@

sources = \
	common.c	\
	model-element.c	\
	classifier.c	\
	comment.c	\
	comment-line.c	\
	actor.c		\
	usecase.c	\
	relationship.c	\
	generalization.c

headers = \
	common.h	\
	model-element.h	\
	classifier.h	\
	comment.h	\
	comment-line.h	\
	actor.h		\
	usecase.h	\
	relationship.h	\
	generalization.c

all-local:
	cp $(srcdir)/.libs/diagramitemsmodule.so $(srcdir)

diagramitemsdir = $(pythondir)
diagramitemsexecdir = $(pyexecdir)

diagramitemsexec_LTLIBRARIES = diagramitemsmodule.la
diagramitemsmodule_la_LDFLAGS = -module -avoid-version -export-symbols-regex initdiagramitems
diagramitemsmodule_la_LIBADD = $(DIACANVAS2_LIBS)
diagramitemsmodule_la_SOURCES = $(sources) diagramitemsmodule.c 
nodist_diagramitemsmodule_la_SOURCES = diagramitems.c

CLEANFILES = diagramitems.c
EXTRA_DIST = diagramitems.defs diagramitems.override
diagramitems.c: diagramitems.defs diagramitems.override

.defs.c:
	(cd $(srcdir) \
	 && $(PYGTK_CODEGEN) \
	    --register $(PYGTK_DEFSDIR)/pango-types.defs \
	    --register $(PYGTK_DEFSDIR)/gdk-types.defs \
	    --register $(PYGTK_DEFSDIR)/gtk-types.defs \
	    --override $*.override \
	    --prefix py$* $*.defs) > gen-$*.c \
	&& cp gen-$*.c $*.c \
	&& rm -f gen-$*.c

