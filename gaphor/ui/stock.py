# vim:sw=4


import gtk
from gaphor.config import GETTEXT_PACKAGE, DATADIR
import gaphor.UML as UML
import os.path as path

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

# Definition of stock items to be added, will be deleted at the end
# of this fils file.
default_stock_items = (
    (STOCK_ACTOR,	'_Actor',	'actor24.png', 'actor16.png'),
    (STOCK_ASSOCIATION,	'A_ssociation',	'association24.png', 'association16.png'),
    (STOCK_CLASS,	'_Class',	'class24.png', 'class16.png'),
    (STOCK_DEPENDENCY,	'_Dependency',	'dependency24.png', 'dependency16.png'),
    (STOCK_DIAGRAM,	'_Diagram',	'diagram24.png', 'diagram16.png'),
    (STOCK_EXTEND,	'_Extend',	None, None),
    (STOCK_COMMENT,	'_Comment',	'comment24.png', 'comment16.png'),
    (STOCK_COMMENT_LINE, 'Comment _line', None, None),
    (STOCK_GENERALIZATION, '_Generalization', 'generalization24.png', 'generalization16.png'),
    (STOCK_INCLUDE,	'_Include',	None, None),
    (STOCK_PACKAGE,	'_Package',	'package24.png', 'package16.png'),
    (STOCK_REALIZATION,	'_Realization',	None, None),
    (STOCK_USECASE,	'_Use case',	'usecase24.png', 'usecase16.png')
)

#default_icon_dir = path.dirname(path.abspath(__file__)) + '/icons/'
default_icon_dir = DATADIR + '/pixmaps/'

print 'default_icon_dir:', default_icon_dir

def get_stock_id(element):
    if issubclass(element, UML.Element):
	try:
	    return uml_to_stock_id_map[element]
	except KeyError:
	    print element, 'not found'
	    pass

#def get_diagram_insert_submenu():
#    xml = '<placeholder name="InsertElement">'
#
#    for stock_id, label, icons in default_stock_items:
#	xml += '<menuitem name="%s" _label="%s" verb="%s" pixtype="stock" pixname="%s"/>' % (stock_id, label, stock_id, stock_id)
#
#    xml += '</placeholder>'
#    return xml

def add_stock_items(stock_items, icon_dir=''):
    icon_factory = GaphorResource(gtk.IconFactory)

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
	    icon_factory.add(si[0], set)
	    #iconlist.append((si[0], set))
	    
    gtk.stock_add(stocklist)

    #for id, set in iconlist:
	#icon_factory.add(id, set)

#
# Initialization:
#
# We should do some special initialization for the icon factory:
icon_factory = GaphorResource(gtk.IconFactory)
icon_factory.add_default()
del icon_factory

add_stock_items(default_stock_items, default_icon_dir)

#assert gtk.stock_lookup(STOCK_ACTOR)

# Remove stock item definitions, GTK+ knows about them, so we don't
# need them anymore...
#del default_stock_items, default_icon_dir

