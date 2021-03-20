
help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/^\([a-z]*\):.*## /  \1\t/' | expand -t14

install:	## Install Gaphor in a local virtual environment
	poetry install

dist: translations	## Build application distribution package
	poetry build

test:		## Run all but slow tests
	poetry run pytest -m "not slow"

test-all:	## Run all tests, including coverage
	poetry run pytest --cov=gaphor/

docs:		## Generate documentation
	poetry run $(MAKE) -C docs html

icons:		## Generate icons from stensil (requires Inkscape)
	$(MAKE) -C gaphor/ui/icons

translations:	## Translate and update .po and .mo files
	poetry run $(MAKE) -C po

## Generate Python model files from Gaphor models
models: gaphor/core/modeling/coremodel.py gaphor/UML/uml.py gaphor/SysML/sysml.py gaphor/C4Model/c4model.py gaphor/RAAML/raaml.py

gaphor/core/modeling/coremodel.py: models/Core.gaphor models/Core.override gaphor/codegen/uml_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	poetry run gaphor/codegen/codegen.py models/Core.gaphor $@ models/Core.override && black $@ && mypy gaphor/core/modeling && isort gaphor/core/modeling/coremodel.py

gaphor/UML/uml.py: models/UML.gaphor models/UML.override gaphor/codegen/uml_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	poetry run gaphor/codegen/codegen.py models/UML.gaphor $@ models/UML.override && mypy gaphor/UML && isort $@ && black $@

gaphor/SysML/sysml.py: models/SysML.gaphor models/SysML.override gaphor/codegen/profile_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	poetry run gaphor/codegen/codegen.py --profile models/SysML.gaphor $@ models/SysML.override && black $@ && isort $@ && mypy gaphor/SysML

gaphor/RAAML/raaml.py: models/FTA.gaphor models/FTA.override gaphor/codegen/profile_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	poetry run gaphor/codegen/codegen.py --profile models/FTA.gaphor $@ models/FTA.override && mypy gaphor/RAAML && isort $@ && black $@

gaphor/C4Model/c4model.py: models/C4Model.gaphor models/C4Model.override gaphor/codegen/profile_coder.py gaphor/codegen/override.py gaphor/codegen/writer.py
	poetry run gaphor/codegen/codegen.py --profile models/C4Model.gaphor $@ models/C4Model.override && mypy gaphor/C4Model && isort $@ && black $@

.PHONY: help dist test docs icons translations models
