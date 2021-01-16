VERSION := $(shell poetry version --no-ansi | cut -d' ' -f2)

help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/^\([a-z]*\):.*## /  \1\t/' | expand -t14

all: dist

pyinstvenv:
	python -m venv pyinstvenv
	pyinstvenv/bin/pip install "../dist/gaphor-${VERSION}-py3-none-any.whl"
	pyinstvenv/bin/pip install tomlkit
	pyinstvenv/bin/pip install pyinstaller==4.2

windows/file_version_info.txt:
	sed "s/__version__/${VERSION}/g" windows/file_version_info.txt.in > windows/file_version_info.txt

gaphor.spec:
	sed "s/__version__/${VERSION}/g" gaphor.spec.in > gaphor.spec

gaphor-script.py:
	pyinstvenv/bin/python make-script.py ../pyproject.toml > gaphor-script.py

dist: pyinstvenv windows/file_version_info.txt gaphor.spec gaphor-script.py
	pyinstvenv/bin/pyinstaller -y gaphor.spec

clean:
	rm -rf dist
	rm -rf build
	rm -f windows/file_version_info.txt
	rm -f gaphor-script.py
	rm -rf pyinstvenv
	rm -f gaphor.spec

.PHONY: clean pyinstvenv all help dist
