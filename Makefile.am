# Require automake-1.6
AUTOMAKE_OPTIONS = 1.6

SUBDIRS = utils doc tests

EXTRA_DIST = $(FILES) $(FILES_FILES) gaphor/config.py.in test-diagram.py

INSTALL_DIRS = $(DIRS)
INSTALL_FILES = $(FILES) gaphor/config.py gaphor/UML/modelelements.py

GEN_UML = $(top_srcdir)/utils/genUML.py
METAMODEL_XMI = $(top_srcdir)/doc/UmlMetaModel.xmi

all-local: gaphor/UML/modelelements.py

gaphor/UML/modelelements.py: $(GEN_UML) $(METAMODEL_XMI)
	$(GEN_UML) $(METAMODEL_XMI) 2>&1 > genmodelelements.py
	-echo "We have our own presentation element class (gaphor.UML.Diagram)"
	grep -v "PresentationElement" genmodelelements.py > gaphor/UML/modelelements.py
	rm -f genmodelelements.py

clean-local:
	find . -name *.py[co] -exec rm -f {} ';'

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
	done

.PHONY: release snapshot

release:
	$(MAKE) dist
	tar zxf $(PACKAGE)-$(VERSION).tar.gz && cd $(PACKAGE)-$(VERSION) && \
	./configure --prefix=$(prefix) && make && cd .. && rm -rf $(PACKAGE)-$(VERSION)

snapshot:
	$(MAKE) dist distdir=$(PACKAGE)`date +"%y%m%d"`

