VERSION := $(shell poetry version --no-ansi | cut -d' ' -f2)

help:		## Show this help
	@echo "make <target>, where <target> is one of:"
	@grep -hP "\t##" $(MAKEFILE_LIST) | sed -e 's/^\([a-z]*\):.*## /  \1\t/' | expand -t14

all: pyinstvenv file_version_info.txt gaphor-script.py dist

pyinstvenv:
	python -m venv pyinstvenv
	pyinstvenv/bin/pip install "../dist/gaphor-${VERSION}-py3-none-any.whl"
	pyinstvenv/bin/pip install pyinstaller==4.1.0


file_version_info.txt:
	sed "s/__version__/$VERSION/g" file_version_info.txt.in > file_version_info.txt

gaphor-script.py:
	python make-script.py ../pyproject.toml > gaphor-script.py

dist: pyinstvenv file_version_info.txt gaphor-script.py
	pyinstvenv/bin/pyinstaller -y gaphor.spec

clean:
	rm -rf dist
	rm -rf build
	rm -rf output
	rm -f file_version_info.txt
	rm -f gaphor-script.py
	rm -rf pyinstvenv

.PHONY: clean pyinstvenv all help dist
