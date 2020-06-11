
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
	block \
	proxyport \
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
	$(INKSCAPE) --export-id=$* --export-id-only --export-text-to-path \
		--export-plain-svg --export-overwrite --export-filename=.$*.svg $< && \
	$(INKSCAPE) --with-gui --batch-process \
		--verb="EditSelectAll;SelectionUnGroup;EditSelectAll;StrokeToPath;FileSave" \
		--export-plain-svg --export-overwrite --export-filename=$@ .$*.svg && rm .$*.svg

.PHONY: all verify
