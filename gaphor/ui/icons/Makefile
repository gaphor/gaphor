
STENSIL=stensil.svg

ICONS=diagram \
	new-diagram \
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
	execution-specification \
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
	import \
	stereotype \
	extension \
	property \
	requirement \
	satisfy \
	derive \
	trace \
	refine \
	verify

ICON_THEME=hicolor/scalable/actions

ICON_FILES=$(patsubst %,$(ICON_THEME)/gaphor-%-symbolic.svg,$(ICONS))
INKSCAPE=flatpak run org.inkscape.Inkscape

all: verify $(ICON_FILES)

verify: stensil.svg
	@for icon in $(ICONS); do grep -q "id=\"$$icon\"" $< || { echo "ERROR: No layer named $$icon"; exit 1; }; done

$(ICON_THEME)/gaphor-%-symbolic.svg: stensil.svg
	$(INKSCAPE) -z --export-id=$* --export-id-only \
		--export-plain-svg=.$*.svg $<
	$(INKSCAPE) --verb EditSelectAll --verb SelectionUnGroup \
		--verb=EditSelectAll --verb StrokeToPath \
		--verb FileSave --verb FileQuit .$*.svg
	$(INKSCAPE) --export-plain-svg=$@ .$*.svg && rm .$*.svg

.PHONY: all verify
