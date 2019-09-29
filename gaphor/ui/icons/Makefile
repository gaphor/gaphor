
STENSIL=stensil.svg

ICONS=diagram \
	pointer \
	box \
	line \
	ellipse \
	comment \
	comment-line \
	class \
	package \
	interface \
	association \
	generalization \
	dependency \
	implementation

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
