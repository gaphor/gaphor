# vim:sw=4
"""Icons that are used by Gaphor.
"""

import os.path
import gtk
import gaphor
import gaphor.UML as UML
from xml.sax import handler
from gaphor.parser import ParserException

XMLNS='http://gaphor.sourceforge.net/gaphor/stock-icons'

# These are not used:
STOCK_POINTER = 'gaphor-pointer'
STOCK_ACTIVITY_FINAL_NODE = 'gaphor-activity-final-node'
STOCK_ACTION = 'gaphor-action'
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
STOCK_COMPONENT = 'gaphor-component'
STOCK_GENERALIZATION = 'gaphor-generalization'
STOCK_IMPLEMENTATION = 'gaphor-implementation'
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


class StockIconLoader(handler.ContentHandler):
    """Load stock icons from an xml file in the icons directory.
    """

    def __init__(self, icon_dir):
        handler.ContentHandler.__init__(self)
	self.icon_dir = icon_dir

    def endDTD(self):
        pass

    def startDocument(self):
        """Start of document: all our attributes are initialized.
        """
	self.id = ''
        self.files = []
        self.data = ''
	self.element = None

    def endDocument(self):
	pass

    def startElement(self, name, attrs):
        self.data = ''

	# A new icon is found
        if name == 'icon':
            self.id = attrs['id']
	    self.files = []
	    self.element = None

	elif name in ('element', 'file', 'stock-icons'):
	    pass
        else:
            raise ParserException, 'Invalid XML: tag <%s> not known' % name

    def endElement(self, name):
        if name == 'icon':
            assert self.id
	    assert self.files
	    add_stock_icon(self.id, self.icon_dir, self.files, self.element)
	elif name == 'element':
	    try:
		self.element = getattr(UML, self.data)
	    except:
		raise ParserException, 'No element found with name %s' % self.data
	elif name == 'file':
	    self.files.append(self.data)
	elif name == 'stock-icons':
	    pass

    def startElementNS(self, name, qname, attrs):
        if not name[0] or name[0] == XMLNS:
            a = { }
            for key, val in attrs.items():
                a[key[1]] = val
            self.startElement(name[1], a)

    def endElementNS(self, name, qname):
        if not name[0] or name[0] == XMLNS:
            self.endElement(name[1])

    def characters(self, content):
        """Read characters."""
	self.data = self.data + content

def load_stock_icons():
    """
    """
    from xml.sax import make_parser
    parser = make_parser()

    data_dir = gaphor.resource('DataDir')
    icon_dir = os.path.join(data_dir, 'pixmaps')
    loader = StockIconLoader(icon_dir)

    parser.setFeature(handler.feature_namespaces, 1)
    parser.setContentHandler(loader)

    parser.parse(os.path.join(data_dir, 'icons.xml'))
    #parser.close()

load_stock_icons()

