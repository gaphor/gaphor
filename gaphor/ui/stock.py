# vim:sw=4


import gtk
from gaphor.config import GETTEXT_PACKAGE, DATADIR
import gaphor.UML as UML
import os.path as path

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
STOCK_PACKAGE = 'gaphor-package'
STOCK_REALIZATION = 'gaphor-realization'
STOCK_USECASE = 'gaphor-usecase'

# Definition of stock items to be added, will be deleted at the end
# of this fils file.
default_stock_icons = (
    (STOCK_POINTER,	'pointer24.png',	'pointer16.png'),
    (STOCK_ACTOR,	'actor24.png',		'actor16.png'),
    (STOCK_ASSOCIATION,	'association24.png',	'association16.png'),
    (STOCK_CLASS,	'class24.png',		'class16.png'),
    (STOCK_DEPENDENCY,	'dependency24.png',	'dependency16.png'),
    (STOCK_DIAGRAM,	'diagram24.png',	'diagram16.png'),
    (STOCK_EXTEND,	None,			None),
    (STOCK_COMMENT,	'comment24.png',	'comment16.png'),
    (STOCK_COMMENT_LINE, None,			None),
    (STOCK_GENERALIZATION, 'generalization24.png', 'generalization16.png'),
    (STOCK_INCLUDE,	None,			None),
    (STOCK_PACKAGE,	'package24.png',	'package16.png'),
    (STOCK_REALIZATION,	None,			None),
    (STOCK_USECASE,	'usecase24.png',	'usecase16.png')
)

uml_to_stock_id_map = {
    UML.Actor: STOCK_ACTOR,
    UML.Association: STOCK_ASSOCIATION,
    UML.Class: STOCK_CLASS,
    UML.Comment: STOCK_COMMENT,
    UML.Dependency: STOCK_DEPENDENCY,
    UML.Diagram: STOCK_DIAGRAM,
    UML.Extend: STOCK_EXTEND,
    UML.Generalization: STOCK_GENERALIZATION,
    UML.Include: STOCK_INCLUDE,
    UML.Package: STOCK_PACKAGE,
    UML.UseCase: STOCK_USECASE
}

def get_stock_id(element):
    if issubclass(element, UML.Element):
	try:
	    return uml_to_stock_id_map[element]
	except KeyError:
	    print element, 'not found'
	    pass

def add_stock_icons(stock_icons, icon_dir=''):
    icon_factory = GaphorResource(gtk.IconFactory)

    #stocklist = []
    iconlist = []

    for si in stock_icons:
	#stocklist.append((si[0], si[1], 0, 0, GETTEXT_PACKAGE))
	#stocklist.append((si[0], si[0], 0, 0, GETTEXT_PACKAGE))
	set = gtk.IconSet()
	do_add=0
	for icon in si[1:]:
	    if icon:
		source = gtk.IconSource()
		source.set_size(gtk.ICON_SIZE_MENU)
		source.set_filename(icon_dir + icon)
		set.add_source(source)
		do_add=1
	if do_add:
	    icon_factory.add(si[0], set)
	    #iconlist.append((si[0], set))
	    
    #gtk.stock_add(stocklist)

    #for id, set in iconlist:
	#icon_factory.add(id, set)

#
# Initialization:
#
# We should do some special initialization for the icon factory:
icon_factory = GaphorResource(gtk.IconFactory)
icon_factory.add_default()
del icon_factory

add_stock_icons(default_stock_icons, DATADIR + '/pixmaps/')

#assert gtk.stock_lookup(STOCK_ACTOR)

# Remove stock item definitions, GTK+ knows about them, so we don't
# need them anymore...
#del default_stock_icons, default_icon_dir

