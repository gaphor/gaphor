# vim:sw=4
"""Manage plugins.
"""

import os.path
import glob
from xml.sax import handler, make_parser
from gaphor import resource
from gaphor.parser import ParserException
from gaphor.misc.action import register_action_for_slot

XMLNS='http://gaphor.sourceforge.net/gaphor/plugin'

# Directories to look for plugins
DEFAULT_PLUGIN_DIRS = [os.path.join(resource('DataDir'), 'plugins'),
		       os.path.join(resource('UserDataDir'), 'plugins')]

class Plugin(object):
    """A plugin represents one plugin loaded from the file system.
    """

    def __init__(self):
	self.required_modules = []
	self.required_plugins = []
	self.required_actions = []
	self.provided_actions = []
	self.initialized = False
	self.path = ''
	self.module = None
	self.status = ''

class PluginAction(object):
    """Each action within a Plugin is represented by a PluginAction.
    """

    def __init__(self, class_, slot):
	self.class_ = class_
	self.slot = slot
	self.id = None
	self.stock_id = None
	self.icon_file = None
	self.tooltip = None
	self.label = None
	self.accel = None
	self.depends = []


class PluginLoader(handler.ContentHandler):
    """Load a Plugin definition file (plugin.xml).
    """
    TOPLEVEL = 0
    REQUIRE = 1
    PROVIDE = 2
    ACTION = 3

    def __init__(self):
        handler.ContentHandler.__init__(self)

    def endDTD(self):
        pass

    def startDocument(self):
        """Start of document: all our attributes are initialized.
        """
	self.plugin = Plugin()
	self.mode = self.TOPLEVEL

    def endDocument(self):
	pass

    def startElement(self, name, attrs):

	mode = self.mode
        if mode == self.TOPLEVEL:
	    if name == 'plugin':
		self.plugin.name = attrs['name']
		self.plugin.version = attrs['version']
		self.plugin.author = attrs['author']
	    if name == 'require':
		self.mode = self.REQUIRE
	    elif name == 'provide':
		self.mode = self.PROVIDE

	elif mode == self.REQUIRE:
	    if name == 'module':
		self.plugin.required_modules.append(attrs['name'])
	    elif name == 'action':
		self.plugin.required_actions.append(attrs['name'])
	    elif name == 'plugin':
		self.plugin.required_plugins.append(attrs['name'])

	elif mode == self.PROVIDE:
	    if name == 'action':
		action = PluginAction(attrs['class'].encode(),
					  attrs['slot'].encode())
		action.id = attrs.get('id', '').encode()
		action.stock_id = attrs.get('stock-id', '').encode()
		action.icon_file = attrs.get('icon-file', '').encode()
		action.tooltip = attrs.get('tooltip', '').encode()
		action.label = attrs.get('label', '').encode()
		action.accel = attrs.get('accel', '').encode()
		self.plugin.provided_actions.append(action)
		self.mode = self.ACTION

	elif mode == self.ACTION:
	    if name == 'depends':
		self.plugin.provided_actions[-1].depends.append(attrs['action'].encode())

        else:
            raise ParserException, 'Invalid XML: tag <%s> not known' % name

    def endElement(self, name):
        if self.mode in (self.REQUIRE, self.PROVIDE) and \
	   name in ('require', 'provide'):
            self.mode = self.TOPLEVEL
	elif self.mode == self.ACTION and name == 'action':
	    self.mode = self.PROVIDE
	elif name in ('plugin', 'module', 'depends'):
	    pass
	else:
            raise ParserException, 'Invalid XML: tag <%s> not known' % name

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
	pass


class PluginManager(object):
    """The PluginManager is the main point where plugins are managed.
    """

    def __init__(self):
	self.plugins = {}
	self.bootstrapped = False

	# Create an XML parser
	self.parser = make_parser()
	self.loader = PluginLoader()
	self.parser.setFeature(handler.feature_namespaces, 1)
	self.parser.setContentHandler(self.loader)

    def bootstrap(self):
	"""Do the normal plugin loading.
	"""
	if self.bootstrapped:
	    return

	for plugin_dir in DEFAULT_PLUGIN_DIRS:
	    self.load_plugins_from_dir(plugin_dir)

	import_done = True
	while import_done:
	    import_done = False
	    for plugin in self.plugins.itervalues():
		if self.requirements_met(plugin):
		    try:
			self.import_plugin(plugin)
		    except Exception, e:
			plugin.status = 'Failed to load plugin %s: %s' % (plugin.name, e)
			log.error('Failed to load plugin %s' % plugin.name, e)
		    else:
			import_done = True

	self.bootstrapped = True

    def load_plugin(self, plugin_xml):
	"""Load a plugin definition and store the plugin in the manager.
	"""
	assert not self.plugins.has_key(os.path.dirname(plugin_xml))
	self.parser.parse(plugin_xml)
	plugin = self.loader.plugin
	plugin.path = os.path.dirname(plugin_xml)
	self.plugins[plugin.name] = plugin

    def load_plugins_from_dir(self, plugin_dir):
	if not os.path.isdir(plugin_dir):
	    return
	for plugin_xml in glob.glob(os.path.join(plugin_dir, '*', 'plugin.xml')):
	    try:
		self.load_plugin(plugin_xml)
	    except Exception, e:
		log.error('Could not load plugin definition %s' % plugin_xml, e)

    def requirements_met(self, plugin):
	"""Check if all <require>-ments are met to load the plugin.
	"""
	if plugin.initialized:
	    return False

	for mod in plugin.required_modules:
	    try:
		# TODO: How to find out if a module exists without loading it?
		__import__(mod, globals(), locals(), [])
	    except ImportError:
		plugin.initialized = True
		plugin.status = 'Could not initialize plugin: module %s could not be imported' % mod
		log.debug(plugin.status)
		return False

	pluginstatus = {}
	for p in self.plugins.itervalues():
	    pluginstatus[p.name] = bool(p.initialized)
	for p in plugin.required_plugins:
	    if not pluginstatus.get(p):
		plugin.status = 'Plugin %s is required by this plugin' % p
		log.debug(plugin.status)
		return False

	return True

    def import_plugin(self, plugin):
	"""Do the actual import of the plugin module.
	"""
	mod = __import__(plugin.path, globals(), locals(), [])
	plugin.module = mod
	plugin.initialized = True
	plugin.status = 'Imported'

	for action in plugin.provided_actions:
	    try:
		self.import_action(action, plugin)
	    except Exception, e:
		log.error('Failed to import action %s' % (action.id or action.class_), e)

    def import_action(self, action, plugin):
	"""Import and register one action in the plugin.
	"""
	# Create an icon for the plugin
	if action.icon_file:
	    from gaphor.ui.stock import add_stock_icon
	    action.stock_id = 'gaphor-plugin-' + action.id
	    add_stock_icon(action.stock_id, plugin.path, [action.icon_file])

	# Fetch the action class
	action_class = getattr(plugin.module, action.class_)

	# Copy attributes from the plugin to the class
	for attr in ('id', 'label', 'stock_id', 'tooltip', 'accel'):
	    val = getattr(action, attr, None)
	    if val:
		setattr(action_class, attr, val)

	register_action_for_slot(action_class, action.slot, *action.depends)
	log.debug('Providing entry %s for slot <%s>' % (action_class, action.slot))

# Make one default plugin manager
import gaphor
_default_plugin_manager = gaphor.resource(PluginManager)
del gaphor

