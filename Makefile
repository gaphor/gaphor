
help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/^\([a-z]*\):.*## /  \1\t/' | expand -t14

dist: test translate	## Build application distribution (requires Poetry)
	poetry build

test:		## Run all but slow tests (requires PyTest)
	pytest -m "not slow"

docs:		## Generate documentation (requirss Sphinx)
	$(MAKE) -C docs html

icons:		## Generate icons from stensil (requires Inkscape)
	$(MAKE) -C gaphor/ui/icons

translate:	## Translate and update .po and .mo files (requires PyBabel)
	$(MAKE) -C po

model: gaphor/UML/uml2.py	## Generate Python model files from Gaphor models (requires Black)

gaphor/UML/uml2.py: gaphor/UML/uml2.gaphor utils/model/gen_uml.py utils/model/override.py utils/model/writer.py
	utils/model/build_uml.py && black $@

.PHONY: help dist test docs icons translate model
