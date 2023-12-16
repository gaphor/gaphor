STENCIL=stencil.svg

ICONS=diagram \
	pointer \
	magnet \
	box \
	line \
	ellipse \
	comment \
	comment-line \
	picture \
	metadata \
	class \
	data-type \
	enumeration \
	primitive-type \
	block \
	interface-block \
	value-specification-action \
	call-behavior-action \
	value-type \
	proxy-port \
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
	activity-parameter-node \
	input-pin \
	output-pin \
	flow-final-node \
	decision-node \
	merge-node \
	fork-node \
	join-node \
	activity \
	state-machine \
	region \
	initial-pseudostate \
	shallow-history-pseudostate \
	deep-history-pseudostate \
	join-pseudostate \
	fork-pseudostate \
	junction-pseudostate \
	choice-pseudostate \
	entry-point-pseudostate \
	exit-point-pseudostate \
	terminate-pseudostate \
	object-node \
	activity-partition \
	control-flow \
	object-flow \
	send-signal-action \
	accept-event-action \
	lifeline \
	behavior-execution-specification \
	execution-specification \
	message \
	reflexive-message \
	interaction \
	state \
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
	derive-reqt \
	trace \
	refine \
	verify \
	allocate \
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

UNAME := $(shell uname)

ifeq ($(UNAME),Darwin)
  INKSCAPE=inkscape
else
  INKSCAPE=flatpak run org.inkscape.Inkscape
endif

all: verify $(ICON_FILES)

verify: stencil.svg
	@for icon in $(ICONS); do grep -q "id=\"$$icon\"" $< || { echo "ERROR: No layer named $$icon"; exit 1; }; done

$(ICON_THEME)/gaphor-%-symbolic.svg: stencil.svg
	$(INKSCAPE) --export-id=$* --export-id-only --export-text-to-path \
		--export-plain-svg --export-overwrite --export-filename=$@ $<

.PHONY: all verify
