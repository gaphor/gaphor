LANGS=ca es fr it nl pt_BR ru sv

SRCS=$(shell find ../gaphor -path ../gaphor/locale -prune -o -print)
MO_FILES=$(patsubst %,../gaphor/locale/%/LC_MESSAGES/gaphor.mo,$(LANGS))

all: $(MO_FILES)

gaphor.pot: $(SRCS)
	pybabel extract -o gaphor.pot -F babel.ini ../gaphor

%.po: gaphor.pot
	pybabel update -i $< -o $@ -l $* -D gaphor

../gaphor/locale/%/LC_MESSAGES/gaphor.mo: %.po
	mkdir -p $$(dirname $@)
	pybabel compile -i $< -o $@ -l $* -D gaphor

.PHONY: all
