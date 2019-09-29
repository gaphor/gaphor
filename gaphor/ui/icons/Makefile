
STENSIL=stensil.svg

ICONS=diagram \
      class \
      package \
      interface \
      association

ICON_FILES=$(patsubst %,gaphor-%-symbolic.svg,$(ICONS))

INKSCAPE=flatpak run org.inkscape.Inkscape

all: $(ICON_FILES)

gaphor-%-symbolic.svg: stensil.svg
	$(INKSCAPE) -z --export-id=$* --export-id-only \
		--export-plain-svg=.$@ $< && \
	$(INKSCAPE) --verb EditSelectAll --verb SelectionUnGroup \
		--verb=EditSelectAll --verb StrokeToPath \
		--verb FileSave --verb FileQuit .$@ && \
	$(INKSCAPE) --export-plain-svg=$@ .$@ && rm .$@
