# vim:sw=4
"""Icons that are used by Gaphor.
"""

import os.path
import gtk
import gaphor
import gaphor.UML as UML

STOCK_POINTER = 'gaphor-pointer'
STOCK_ACTOR = 'gaphor-actor'
STOCK_ASSOCIATION = 'gaphor-association'
STOCK_CLASS = 'gaphor-class'
STOCK_COMMENT = 'gaphor-comment'
STOCK_COMMENT_LINE = 'gaphor-comment-line'
STOCK_DEPENDENCY = 'gaphor-dependency'
STOCK_DIAGRAM = 'gaphor-diagram'
STOCK_EXTEND = 'gaphor-extend'
STOCK_GENERALIZATION = 'gaphor-generalization'
STOCK_INCLUDE = 'gaphor-include'
STOCK_OPERATION = 'gaphor-operation'
STOCK_PACKAGE = 'gaphor-package'
STOCK_PROPERTY = 'gaphor-property'
STOCK_REALIZATION = 'gaphor-realization'
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

def add_stock_icon(id, icon_dir, icon_files, uml_class=None):
    global _uml_to_stock_id_map
    global _icon_factory
    set = gtk.IconSet()
    for icon in icon_files:
	source = gtk.IconSource()
	source.set_size(gtk.ICON_SIZE_MENU)
	source.set_filename(os.path.join(icon_dir, icon))
	set.add_source(source)
    _icon_factory.add(id, set)
    if uml_class:
	_uml_to_stock_id_map[uml_class] = id

icon_dir = os.path.join(gaphor.resource('DataDir'), 'pixmaps')

# Initialize stock icons:
add_stock_icon(STOCK_POINTER,	icon_dir, ('pointer24.png', 'pointer16.png'))
add_stock_icon(STOCK_ACTOR,	icon_dir, ('actor24.png', 'actor16.png'), UML.Actor)
add_stock_icon(STOCK_ASSOCIATION, icon_dir, ('association24.png', 'association16.png'), UML.Association)
add_stock_icon(STOCK_CLASS,	icon_dir, ('class24.png', 'class16.png'), UML.Class)
add_stock_icon(STOCK_DEPENDENCY, icon_dir, ('dependency24.png', 'dependency16.png'), UML.Dependency)
add_stock_icon(STOCK_DIAGRAM,	icon_dir, ('diagram24.png', 'diagram16.png'), UML.Diagram)
add_stock_icon(STOCK_COMMENT,	icon_dir, ('comment24.png', 'comment16.png'), UML.Comment)
add_stock_icon(STOCK_COMMENT_LINE, icon_dir, ('commentline24.png', 'commentline16.png'))
add_stock_icon(STOCK_GENERALIZATION, icon_dir, ('generalization24.png', 'generalization16.png'), UML.Generalization)
add_stock_icon(STOCK_OPERATION,	icon_dir, ('pointer24.png', 'pointer16.png'), UML.Operation)
add_stock_icon(STOCK_PACKAGE,	icon_dir, ('package24.png', 'package16.png'), UML.Package)
add_stock_icon(STOCK_PROPERTY,	icon_dir, ('pointer24.png', 'pointer16.png'), UML.Property)
add_stock_icon(STOCK_USECASE,	icon_dir, ('usecase24.png', 'usecase16.png'), UML.UseCase)

del icon_dir

