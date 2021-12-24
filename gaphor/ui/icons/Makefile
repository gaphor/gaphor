MAKEFLAGS += -j4

STENSIL=stensil.svg

ICONS=diagram \
	new-diagram \
	pointer \
	magnet \
	box \
	line \
	ellipse \
	comment \
	comment-line \
	class \
	data-type \
	enumeration \
	primitive \
	block \
	value-type \
	proxyport \
	package \
	containment \
	interface \
	association \
	composite-association \
	shared-association \
	generalization \
	dependency \
	usage \
	realization \
	interface-realization \
	component \
	artifact \
	node \
	device \
	connector \
	information-flow \
	action \
	initial-node \
	activity-final-node \
	flow-final-node \
	decision-node \
	fork-node \
	join-node \
	activity \
	state-machine \
	region \
	object-node \
	activity-partition \
	control-flow \
	send-signal-action \
	accept-event-action \
	lifeline \
	behavior-execution-specification \
	execution-specification \
	message \
	reflexive-message \
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
	item-flow \
	requirement \
	satisfy \
	derive \
	trace \
	refine \
	verify \
	constraint \
	view-editor \
	c4-person \
	c4-software-system \
	c4-container \
	c4-database \
	c4-component \
	and \
	or \
	not \
	seq \
	xor \
	majority_vote \
	transfer-in \
	transfer-out \
	inhibit \
	basic-event \
	conditional-event \
	dormant-event \
	undeveloped-event \
	house-event \
	zero-event \
	top-event \
	intermediate-event \
	loss \
	hazard \
	situation \
	controller \
	actuator \
	controlled-process \
	abstract-operational-situation \
	operational-situation \
	unsafe-control-action \
	relevant-to \
	control-action \
	control-structure


ICON_THEME=hicolor/scalable/actions

ICON_FILES=$(patsubst %,$(ICON_THEME)/gaphor-%-symbolic.svg,$(ICONS))
INKSCAPE=flatpak run org.inkscape.Inkscape

all: verify $(ICON_FILES)

verify: stensil.svg
	@for icon in $(ICONS); do grep -q "id=\"$$icon\"" $< || { echo "ERROR: No layer named $$icon"; exit 1; }; done

$(ICON_THEME)/gaphor-%-symbolic.svg: stensil.svg
	$(INKSCAPE) --export-id=$* --export-id-only --export-text-to-path \
		--export-plain-svg --export-overwrite --export-filename=$@ $<

.PHONY: all verify
