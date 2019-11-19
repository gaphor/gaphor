
help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/:.*##/    /' | expand -t20


docs:		## Generate documentation (requirss Sphinx)
	$(MAKE) -C docs html

translate:	## Translate and update .po and .mo files (requires PyBabel)
	$(MAKE) -C po

icons:		## Generate icons from stensil (requires Inkscape)
	$(MAKE) -C gaphor/ui/icons

.PHONY: help docs translate icons