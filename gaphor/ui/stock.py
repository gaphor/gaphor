# vim:sw=4
"""Icons that are used by Gaphor.
"""

import os.path
import gtk
import gaphor
import gaphor.UML as UML

STOCK_POINTER = 'gaphor-pointer'
STOCK_ACTIVITY_FINAL_NODE = 'gaphor-activity-final-node'
STOCK_ACTOR = 'gaphor-actor'
STOCK_ASSOCIATION = 'gaphor-association'
STOCK_CLASS = 'gaphor-class'
STOCK_COMMENT = 'gaphor-comment'
STOCK_COMMENT_LINE = 'gaphor-comment-line'
STOCK_DECISION_NODE = 'gaphor-decision-node'
STOCK_DEPENDENCY = 'gaphor-dependency'
STOCK_DIAGRAM = 'gaphor-diagram'
STOCK_EXTEND = 'gaphor-extend'
STOCK_EXTENSION = 'gaphor-extension'
STOCK_CONTROL_FLOW = 'gaphor-control-flow'
STOCK_GENERALIZATION = 'gaphor-generalization'
STOCK_INCLUDE = 'gaphor-include'
STOCK_INITIAL_NODE = 'gaphor-initial-node'
STOCK_OPERATION = 'gaphor-operation'
STOCK_PACKAGE = 'gaphor-package'
STOCK_PROFILE = 'gaphor-profile'
STOCK_PARAMETER = 'gaphor-parameter'
STOCK_PROPERTY = 'gaphor-property'
STOCK_REALIZATION = 'gaphor-realization'
STOCK_STEREOTYPE = 'gaphor-stereotype'
STOCK_USECASE = 'gaphor-usecase'

_icon_factory = gtk.IconFactory()
_icon_factory.add_default()

_uml_to_stock_id_map = { }

def get_stock_id(element):
    if issubclass(element, UML.Element):
	try:
	    return _uml_to_stock_id_map[element]
	except KeyError:
	    log.warning ('Stock id for %s not found' % element)
	    return STOCK_POINTER

def add_stock_icon(id, icon_dir, icon_files, uml_class=None):
    global _uml_to_stock_id_map
    global _icon_factory
    set = gtk.IconSet()
    for icon in icon_files:
	source = gtk.IconSource()
	if icon.find('16') != -1:
	    source.set_size(gtk.ICON_SIZE_MENU)
	elif icon.find('24') != -1:
	    source.set_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
	elif icon.find('48') != -1:
	    source.set_size(gtk.ICON_SIZE_LARGE_TOOLBAR)
	source.set_filename(os.path.join(icon_dir, icon))
	set.add_source(source)
    _icon_factory.add(id, set)
    if uml_class:
	_uml_to_stock_id_map[uml_class] = id

icon_dir = os.path.join(gaphor.resource('DataDir'), 'pixmaps')

# Initialize stock icons:
add_stock_icon(STOCK_POINTER,	icon_dir, ('pointer24.png',))

add_stock_icon(STOCK_ACTIVITY_FINAL_NODE, icon_dir, ('activityfinalnode24.png',), UML.ActivityFinalNode)
add_stock_icon(STOCK_ACTOR,	icon_dir, ('actor24.png',), UML.Actor)
add_stock_icon(STOCK_ASSOCIATION, icon_dir, ('association24.png',), UML.Association)
add_stock_icon(STOCK_CLASS,	icon_dir, ('class24.png',), UML.Class)
add_stock_icon(STOCK_COMMENT,	icon_dir, ('comment24.png',), UML.Comment)
add_stock_icon(STOCK_COMMENT_LINE, icon_dir, ('commentline24.png',))
add_stock_icon(STOCK_CONTROL_FLOW,	icon_dir, ('controlflow24.png',), UML.ControlFlow)
add_stock_icon(STOCK_DECISION_NODE, icon_dir, ('decisionnode24.png',), UML.DecisionNode)
add_stock_icon(STOCK_DEPENDENCY, icon_dir, ('dependency24.png',), UML.Dependency)
add_stock_icon(STOCK_DIAGRAM,	icon_dir, ('diagram16.png',), UML.Diagram)
add_stock_icon(STOCK_EXTENSION, icon_dir, ('extension24.png',), UML.Extension)
add_stock_icon(STOCK_GENERALIZATION, icon_dir, ('generalization24.png',), UML.Generalization)
add_stock_icon(STOCK_INITIAL_NODE, icon_dir, ('initialnode24.png',), UML.InitialNode)
add_stock_icon(STOCK_OPERATION,	icon_dir, ('pointer24.png',), UML.Operation)
add_stock_icon(STOCK_PACKAGE,	icon_dir, ('package24.png',), UML.Package)
add_stock_icon(STOCK_PARAMETER,	icon_dir, ('pointer24.png',), UML.Parameter)
add_stock_icon(STOCK_PROFILE,	icon_dir, ('package24.png',), UML.Profile)
add_stock_icon(STOCK_PROPERTY,	icon_dir, ('pointer24.png',), UML.Property)
add_stock_icon(STOCK_STEREOTYPE, icon_dir, ('stereotype24.png',), UML.Stereotype)
add_stock_icon(STOCK_USECASE,	icon_dir, ('usecase24.png',), UML.UseCase)

del icon_dir

