# vim:sw=4


import gtk
from gaphor.config import GETTEXT_PACKAGE
import gaphor.UML as UML
import os.path as path

STOCK_ACTOR = 'gaphor-actor'
STOCK_USECASE = 'gaphor-usecase'
STOCK_PACKAGE = 'gaphor-package'
STOCK_COMMENT = 'gaphor-comment'
STOCK_COMMENT_LINE = 'gaphor-comment-line'
STOCK_GENERALIZATION = 'gaphor-generalization'
STOCK_ASSOCIATION = 'gaphor-association'
STOCK_DEPENDENCY = 'gaphor-dependency'
STOCK_REALIZATION = 'gaphor-realization'
STOCK_INCLUDE = 'gaphor-include'
STOCK_EXTEND = 'gaphor-extend'
STOCK_DIAGRAM = 'gaphor-diagram'

uml_to_stock_id_map = {
    UML.Actor: STOCK_ACTOR,
    UML.UseCase: STOCK_USECASE,
    UML.Package: STOCK_PACKAGE,
    UML.Comment: STOCK_COMMENT,
    UML.Generalization: STOCK_GENERALIZATION,
    UML.Association: STOCK_ASSOCIATION,
    UML.Dependency: STOCK_DEPENDENCY,
    UML.Include: STOCK_INCLUDE,
    UML.Extend: STOCK_EXTEND,
    UML.Diagram: STOCK_DIAGRAM
}

# Definition of stock items to be added, will be deleted at the end
# of this fils file.
default_stock_items = (
    (STOCK_DIAGRAM,	'_Diagram',	'diagram24.png', 'diagram16.png'),
    (STOCK_ACTOR,	'_Actor',	'actor24.png', 'actor16.png'),
    (STOCK_USECASE,	'_Use case',	'usecase24.png', 'usecase16.png'),
    (STOCK_PACKAGE,	'_Package',	'package24.png', 'package16.png'),
    (STOCK_COMMENT,	'_Comment',	'comment24.png', 'comment16.png'),
    (STOCK_COMMENT_LINE, 'Comment _line', None, None),
    (STOCK_GENERALIZATION, '_Generalization', 'generalization24.png', 'generalization16.png'),
    (STOCK_ASSOCIATION,	'A_ssociation',	'association24.png', 'association16.png'),
    (STOCK_DEPENDENCY,	'_Dependency',	'dependency24.png', 'dependency16.png'),
    (STOCK_REALIZATION,	'_Realization',	None, None),
    (STOCK_INCLUDE,	'_Include',	None, None),
    (STOCK_EXTEND,	'_Extend',	None, None)
)

default_icon_dir = path.dirname(path.abspath(__file__)) + '/icons/'

print 'default_icon_dir:', default_icon_dir

def get_stock_id(element):
    if issubclass(element, UML.Element):
	try:
	    return uml_to_stock_id_map[element]
	except KeyError:
	    print element, 'not found'
	    pass

def add_stock_items(stock_items, icon_dir=''):
    icon_factory = gaphorResource(gtk.IconFactory)

    stocklist = []
    iconlist = []

    for si in stock_items:
	stocklist.append((si[0], si[1], 0, 0, GETTEXT_PACKAGE))
	set = gtk.IconSet()
	do_add=0
	for icon in si[2:]:
	    if icon:
		source = gtk.IconSource()
		source.set_size(gtk.ICON_SIZE_MENU)
		source.set_filename(icon_dir + icon)
		set.add_source(source)
		do_add=1
	if do_add:
	    iconlist.append((si[0], set))
	    
    gtk.stock_add(stocklist)

    for id, set in iconlist:
	icon_factory.add(id, set)

#
# Initialization:
#
# We should do some special initialization for the icon factory:
icon_factory = gaphorResource(gtk.IconFactory)
icon_factory.add_default()
del icon_factory

add_stock_items(default_stock_items, default_icon_dir)

# Remove stock item definitions, GTK+ knows about them, so we don't
# need them anymore...
del default_stock_items, default_icon_dir

