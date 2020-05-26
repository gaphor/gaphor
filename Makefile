
help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/^\([a-z]*\):.*## /  \1\t/' | expand -t14

dist: translations	## Build application distribution (requires Poetry)
	poetry build

test:		## Run all but slow tests (requires PyTest)
	pytest -m "not slow"

docs:		## Generate documentation (requirss Sphinx)
	$(MAKE) -C docs html

icons:		## Generate icons from stensil (requires Inkscape)
	$(MAKE) -C gaphor/ui/icons

translations:	## Translate and update .po and .mo files (requires PyBabel)
	$(MAKE) -C po

models: gaphor/core/modeling/coremodel.py gaphor/UML/uml.py gaphor/SysML/sysml.py	## Generate Python model files from Gaphor models (requires Black, MyPy)

gaphor/core/modeling/coremodel.py: models/Core.gaphor models/Core.override gaphor/codegen/uml_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	gaphor/codegen/codegen.py models/Core.gaphor gaphor/core/modeling/coremodel.py models/Core.override && black $@ && mypy gaphor/core/modeling && isort gaphor/core/modeling/coremodel.py

gaphor/UML/uml.py: models/UML.gaphor models/UML.override gaphor/codegen/uml_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	gaphor/codegen/codegen.py models/UML.gaphor gaphor/UML/uml.py models/UML.override && mypy gaphor/UML && isort $@ && black $@

gaphor/SysML/sysml.py: models/SysML.gaphor models/SysML.override gaphor/codegen/profile_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	gaphor/codegen/codegen.py --profile models/SysML.gaphor gaphor/SysML/sysml.py models/SysML.override && black $@ && isort $@ && mypy gaphor/SysML

gaphor/Safety/safety.py: models/Safety.gaphor models/Safety.override gaphor/codegen/profile_coder.py.py gaphor/codegen/override.py gaphor/codegen/writer.py
	gaphor/codegen/codegen.py --profile models/Safety.gaphor gaphor/Safety/safety.py models/Safety.override && mypy gaphor/Safety && isort $@ && black $@

.PHONY: help dist test docs icons translations models
