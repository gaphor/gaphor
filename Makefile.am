# Require automake-1.6
AUTOMAKE_OPTIONS = 1.6

# The definition of 'DIRS' and 'FILES' is defined by 'configure'...
# DIRS: The subdirectories that should be added to the distribution.
# FILES: The files named 'Files' that contain (Python) files that should be
#	 added to the distribution.

SUBDIRS = data utils po doc tests

bin_SCRIPTS = bin/gaphor

EXTRA_DIST = $(FILES) $(FILES_FILES) gaphor.sh bin/gaphor.in gaphor/config.py.in

INSTALL_DIRS = $(DIRS)
INSTALL_FILES = $(FILES) gaphor/config.py gaphor/UML/modelelements.py

GEN_UML = $(top_srcdir)/utils/genUML.py
METAMODEL_XMI = $(top_srcdir)/doc/UmlMetaModel.xmi

# Makefile depends on the 'Files' files, so we should add them as a dependency
# to reconfigure...
CONFIG_STATUS_DEPENDENCIES = $(FILES_FILES)

all-local: gaphor/UML/modelelements.py

gaphor/UML/modelelements.py: $(GEN_UML) $(METAMODEL_XMI)
	$(GEN_UML) $(METAMODEL_XMI) > genmodelelements.py
	mv genmodelelements.py gaphor/UML/modelelements.py

clean-local:
	find . -name *.py[co] -exec rm -f {} ';'
	rm -f gaphor/UML/modelelements.py

INSTALLDIR=$(DESTDIR)$(pythondir)/

install-exec-local:
	for D in $(INSTALL_DIRS); do \
		$(mkinstalldirs) $(INSTALLDIR)$$D; \
	done; \
	for F in $(INSTALL_FILES); do \
		echo " $(INSTALL_DATA) $(srcdir)/$$F $(INSTALLDIR)$$F"; \
		$(INSTALL_DATA) $(srcdir)/$$F $(INSTALLDIR)$$F; \
	done; \
	PYTHON=$(PYTHON) $(top_srcdir)/py-compile --basedir $(INSTALLDIR) $(INSTALL_FILES)

uninstall-local:
	for D in $(INSTALL_DIRS); do \
		test -d "$(INSTALLDIR)$$D" && rm -rf "$(INSTALLDIR)$$D"; \
	done; true

.PHONY: release snapshot files-check potfiles.in

release:
	$(MAKE) dist
	tar zxf $(PACKAGE)-$(VERSION).tar.gz && cd $(PACKAGE)-$(VERSION) && \
	./configure --prefix=$(prefix) && make && cd .. && rm -rf $(PACKAGE)-$(VERSION)

snapshot:
	$(MAKE) dist distdir=$(PACKAGE)`date +"%y%m%d"`

files-check:
	@for F in `find gaphor -name '*.py' -o -name '*.png'`; do \
		{ echo "$(FILES)" | grep -q "\<$$F\>"; } || echo "Missing file: $$F"; \
	done

potfiles.in:
	for L in $(FILES); do \
		echo "$$L"; \
	done | grep '\.py$$' > $(srcdir)/po/POTFILES.in

