
SUBDIRS=gaphor utils doc

.PHONY: release snapshot

release:
	$(MAKE) dist
	tar zxf $(PACKAGE)-$(VERSION).tar.gz && cd $(PACKAGE)-$(VERSION) && \
	./configure && make && cd .. && rm -rf $(PACKAGE)-$(VERSION)

snapshot:
	$(MAKE) dist distdir=$(PACKAGE)`date +"%y%m%d"`

