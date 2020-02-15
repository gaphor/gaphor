
help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/^\([a-z]*\):.*## /  \1\t/' | expand -t14

dist: icons translate	## Build application distribution (requires Poetry)
	poetry build

docs:		## Generate documentation (requirss Sphinx)
	$(MAKE) -C docs html

icons:		## Generate icons from stensil (requires Inkscape)
	$(MAKE) -C gaphor/ui/icons

translate:	## Translate and update .po and .mo files (requires PyBabel)
	$(MAKE) -C po

.PHONY: help dist docs icons translate
