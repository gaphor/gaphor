# Require automake-1.5
AUTOMAKE_OPTIONS = 1.5

SUBDIRS = gaphor utils doc tests

.PHONY: release snapshot

release:
	$(MAKE) dist
	tar zxf $(PACKAGE)-$(VERSION).tar.gz && cd $(PACKAGE)-$(VERSION) && \
	./configure --prefix=$(prefix) && make && cd .. && rm -rf $(PACKAGE)-$(VERSION)

snapshot:
	$(MAKE) dist distdir=$(PACKAGE)`date +"%y%m%d"`

