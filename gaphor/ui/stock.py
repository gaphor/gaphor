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
_default_stock_icons = (
    # Stock ID		UML class	Icon 1		Icon 2
    (STOCK_POINTER,	None,		'pointer24.png', 'pointer16.png'),
    (STOCK_ACTOR,	UML.Actor,	'actor24.png', 'actor16.png'),
    (STOCK_ASSOCIATION,	UML.Association, 'association24.png', 'association16.png'),
    (STOCK_CLASS,	UML.Class,	'class24.png', 'class16.png'),
    (STOCK_DEPENDENCY,	UML.Dependency, 'dependency24.png', 'dependency16.png'),
    (STOCK_DIAGRAM,	UML.Diagram,	'diagram24.png', 'diagram16.png'),
    (STOCK_EXTEND,	UML.Extend,	None),
    (STOCK_COMMENT,	UML.Comment,	'comment24.png', 'comment16.png'),
    (STOCK_COMMENT_LINE, None,		None),
    (STOCK_GENERALIZATION, UML.Generalization, 'generalization24.png', 'generalization16.png'),
    (STOCK_INCLUDE,	UML.Include,	None),
    (STOCK_PACKAGE,	UML.Package,	'package24.png', 'package16.png'),
    (STOCK_REALIZATION,	None,		None),
    (STOCK_USECASE,	UML.UseCase,	'usecase24.png', 'usecase16.png')
)

_icon_factory = gtk.IconFactory()
_icon_factory.add_default()
_uml_to_stock_id_map = dict()

def get_stock_id(element):
    if issubclass(element, UML.Element):
	try:
	    return _uml_to_stock_id_map[element]
	except KeyError:
	    log.warning ('Stock id for %s not found' % element)

def add_stock_icons(stock_icons, icon_dir=''):
    global _uml_to_stock_id_map
    global _icon_factory
    #icon_factory = GaphorResource(gtk.IconFactory)
    iconlist = []

    for si in stock_icons:
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
	    _icon_factory.add(si[0], set)
	if si[1]:
	    _uml_to_stock_id_map[si[1]] = si[0]

#
# Initialization:
#
# We should do some special initialization for the icon factory:
#icon_factory = gtk.IconFactory() #GaphorResource(gtk.IconFactory)
#icon_factory.add_default()
#del icon_factory

add_stock_icons(_default_stock_icons, DATADIR + '/pixmaps/')

