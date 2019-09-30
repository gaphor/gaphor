
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
	implementation \
	component \
	artifact \
	node \
	device \
	connector \
	action \
	initial-node \
	activity-final-node \
	flow-final-node \
	decision-node \
	fork-node \
	object-node \
	partition \
	control-flow \
	send-signal-action \
	accept-event-action \
	lifeline \
	message \
	interaction \
	state \
	initial-pseudostate \
	pseudostate \
	final-state \
	transition \
	use-case \
	actor \
	include \
	extend \
	profile \
	metaclass \
	stereotype \
	extension \
	property

ICON_FILES=$(patsubst %,gaphor-%-symbolic.svg,$(ICONS))

INKSCAPE=flatpak run org.inkscape.Inkscape

all: verify $(ICON_FILES)

verify: stensil.svg
	@for icon in $(ICONS); do grep -q "id=\"$$icon\"" $< || { echo "ERROR: No layer named $$icon"; exit 1; }; done

gaphor-%-symbolic.svg: stensil.svg
	$(INKSCAPE) -z --export-id=$* --export-id-only \
		--export-plain-svg=.$@ $<
	$(INKSCAPE) --verb EditSelectAll --verb SelectionUnGroup \
		--verb=EditSelectAll --verb StrokeToPath \
		--verb FileSave --verb FileQuit .$@
	$(INKSCAPE) --export-plain-svg=$@ .$@ && rm .$@

.PHONY: all verify
