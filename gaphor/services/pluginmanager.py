"""
Plugin Manager.

The plugin manager is used to manage (register/unregister) plugins.

A Plugin is presented as a directory. This directory contains two files:
 - plugin.xml contains a description of the plugin
 - __init__.py is needed since the plugin is loaded as a module
 
The following classes are provided by this module:

PluginManager - The main class. PluginManager.bootstrap() loads all plugins
        from the default plugin dirs ($PREFIX/share/gaphor/plugins and
        $HOME/.gaphor/plugins).
Plugin - This class represents a plugin. It contains data from plugin.xml
        as well as data gathered during the plugin loading process (such as
        the module that was created when the plugin is imported.
PluginAction - Defines an gaphor.plugin.Action instance.
PluginLoader - SAX parser used to read the plugin.xml file of a plugin. This
        class creates a Plugin instance from the xml file.

User provided plugins overrule the system provided plugins.
"""
import imp
import os
import os.path
import glob
import sys
import pkg_resources
from xml.sax import handler, make_parser

from zope import interface
from gaphor.interfaces import IService

from gaphor.parser import ParserException
from gaphor.misc.action import register_action_for_slot
from gaphor.misc.odict import odict


XMLNS='http://gaphor.sourceforge.net/gaphor/plugin'
MODULENS='gaphor._plugins.'

# Directories to look for plugins. These sirectories are added to the
# search path. User provided plugins overrule system plugins.
# TODO: fix:
#DEFAULT_PLUGIN_DIRS = [os.path.join(resource('DataDir'), 'plugins'),
#                       os.path.join(resource('UserDataDir'), 'plugins')]

#log.debug('sys.path=' + str(sys.path))
#log.debug('DEFAULT_PLUGIN_DIRS=' + str(DEFAULT_PLUGIN_DIRS))

class Plugin(object):
    """
    A plugin represents one plugin loaded from the file system.
    """

    def __init__(self):
        self.required_modules = []
        self.required_plugins = []
        self.required_actions = []
        self.provided_actions = []
        self.description = ''
        self.initialized = False
        self.path = ''
        self.module = None
        self.status = ''

    def requirements_met(self, manager):
        """
        Check if all <require>-ments are met to load the plugin.
        """
        if self.initialized:
            return False

        for mod in self.required_modules:
            try:
                # TODO: How to find out if a module exists without loading it?
                __import__(mod, globals(), locals(), [])
            except ImportError:
                self.initialized = True
                self.status = 'Could not initialize plugin: required module %s could not be imported' % mod
                log.debug(self.status)
                return False

        pluginstatus = {}
        for p in manager.plugins.itervalues():
            pluginstatus[p.name] = bool(p.initialized)
        for p in self.required_plugins:
            if not pluginstatus.get(p):
                self.status = 'Plugin %s is a prerequisite' % p
                log.debug(self.status + ' for %s' % self.name)
                return False

        return True

    def import_plugin(self, importer):
        """
        Do the actual import of the plugin module.
        """
        #mod = __import__(self.path.split(os.sep)[-1], globals(), locals(), [])
        name = os.path.split(self.path)[1]

        mod = importer(name)
        self.module = mod
        self.initialized = True
        if mod:
            self.status = 'Imported'

        #log.debug('Trying to import %d actions' % len(self.provided_actions))
        for action in self.provided_actions:
            try:
                #log.debug('Trying to import action %s' % action.id)
                action.import_action(self)
            except Exception, e:
                self.status += '\nFailed to import action %s (%s)' % (action.id or action.class_, e)
                log.error('Failed to import action %s' % (action.id or action.class_), e)


class PluginAction(object):
    """
    Each action within a Plugin is represented by a PluginAction.
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

    def import_action(self, plugin):
        """
        Import and register one action in the plugin.
        """
        # Create an icon for the plugin
        if self.icon_file:
            from gaphor.ui.stock import add_stock_icon
            self.stock_id = 'gaphor-plugin-' + self.id
            add_stock_icon(self.stock_id, plugin.path, [self.icon_file])

        # Fetch the action class
        action_class = getattr(plugin.module, self.class_)

        # Copy attributes from the plugin to the class
        for attr in ('id', 'label', 'stock_id', 'tooltip', 'accel'):
            val = getattr(self, attr, None)
            if val:
                setattr(action_class, attr, val)

        register_action_for_slot(action_class, self.slot, *self.depends)
        log.debug('Providing action %s for slot %s' % (action_class, self.slot))

class PluginLoader(handler.ContentHandler):
    """
    Load a Plugin definition file (plugin.xml).
    """

    # A typical plugin.xml file might look like this:
    # <?xml version="1.0"?>                            ## mode => TOPLEVEL
    # <gaphor-plugin name="UML metamodel sanity check" ## mode => PLUGIN
    #         version="0.1"
    #         author="Arjan Molenaar">
    #   <description>                                  ## mode => DESCRIPTION
    #     ...
    #   </description>                                 ## mode <= PLUGIN
    #
    #   <require>                                      ## mode => REQUIRE
    #     <module name="os.path"/>
    #     <plugin name="Test plugin"/>
    #   </require>                                     ## mode <= PLUGIN
    #
    #   <provide>                                      ## mode => PROVIDE
    #     <action id="CheckMetamodel"                  ## mode => ACTION
    #             label="Check UML metamodel"
    #             tooltip="Check the UML meta model for errors"
    #             class="CheckMetamodelAction" slot="WindowSlot">
    #       <depends action=""/>
    #     </action>                                    ## mode <= PROVIDE
    #
    #   </provide>                                     ## mode <= PLUGIN
    # </gaphor-plugin>                                 ## mode <= TOPLEVEL

    TOPLEVEL = 0
    PLUGIN = 1
    REQUIRE = 2
    PROVIDE = 3
    ACTION = 4
    DESCRIPTION = 5

    def __init__(self):
        handler.ContentHandler.__init__(self)

    def endDTD(self):
        pass

    def startDocument(self):
        """
        Start of document: all our attributes are initialized.
        """
        self.plugin = Plugin()
        self.mode = self.TOPLEVEL

    def endDocument(self):
        assert self.mode == self.TOPLEVEL

    def startElement(self, name, attrs):
        mode = self.mode
        if mode == self.TOPLEVEL:
            if name == 'gaphor-plugin':
                self.plugin.name = attrs['name']
                self.plugin.version = attrs['version']
                self.plugin.author = attrs['author']
                self.mode = self.PLUGIN
            else:
                raise ParserException, 'Invalid XML: expecting <gaphor-plugin>. Got <%s>.' % name

        elif mode == self.PLUGIN:
            if name == 'description':
                self.mode = self.DESCRIPTION
            elif name == 'require':
                self.mode = self.REQUIRE
            elif name == 'provide':
                self.mode = self.PROVIDE
            else:
                raise ParserException, 'Invalid XML: expecting <description>, <require> or <provide>. Got <%s>.' % name

        elif mode == self.REQUIRE:
            if name == 'module':
                self.plugin.required_modules.append(attrs['name'])
            elif name == 'action':
                self.plugin.required_actions.append(attrs['name'])
            elif name == 'plugin':
                self.plugin.required_plugins.append(attrs['name'])
            else:
                raise ParserException, 'Invalid XML: expecting <module>, <action> or <plugin>. Got <%s>.' % name

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
            else:
                raise ParserException, 'Invalid XML: expecting <action>. Got <%s>.' % name

        elif mode == self.ACTION:
            if name == 'depends':
                self.plugin.provided_actions[-1].depends.append(attrs['action'].encode())
            else:
                raise ParserException, 'Invalid XML: expecting <depends>. Got <%s>.' % name

        else:
            raise ParserException, 'Invalid XML: tag <%s> not known' % name

    def endElement(self, name):
        if self.mode in (self.REQUIRE, self.PROVIDE, self.DESCRIPTION) and \
           name in ('description', 'require', 'provide'):
            self.mode = self.PLUGIN
        elif self.mode == self.ACTION and name == 'action':
            self.mode = self.PROVIDE
        elif self.mode == self.PLUGIN and name == 'gaphor-plugin':
            self.mode = self.TOPLEVEL
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
        if self.mode == self.DESCRIPTION:
            self.plugin.description += content


class PluginManager(object):
    """
    The PluginManager is the main point where plugins are managed.
    """

    interface.implements(IService)

    def __init__(self):
        self.plugins = odict()
        self.bootstrapped = False

        # Create an XML parser
        self.parser = make_parser()
        self.loader = PluginLoader()
        self.parser.setFeature(handler.feature_namespaces, 1)
        self.parser.setContentHandler(self.loader)

    def init(self, app):
        self._app = app
        self.bootstrap()

    def shutdown(self):
        pass

    def bootstrap(self):
        """
        Do the normal plugin loading.
        """
        if self.bootstrapped:
            return

        plugin_dir = pkg_resources.resource_filename('gaphor', 'data/plugins')

        # Load the plugins in reverse order, so the user plugins will
        # overwrite the default plugins. (they are imported in sys.path as
        # [user plugins, default plugins]).
        #for plugin_dir in plugin_dir:
        self.load_plugins_from_dir(plugin_dir)

        def plugin_importer(name):
            f, n, d = imp.find_module(name, [plugin_dir])
            return imp.load_module(MODULENS + name, f, n, d)

        import_done = True
        while import_done:
            import_done = False
            for plugin in self.plugins.itervalues():
                if plugin.requirements_met(self):
                    try:
                        plugin.import_plugin(plugin_importer)
                    except Exception, e:
                        plugin.status = 'Failed to load plugin %s: %s' % (plugin.name, e)
                        log.error('Failed to load plugin %s' % plugin.name, e)
                    else:
                        import_done = True

        self.bootstrapped = True

    def load_plugin(self, plugin_xml):
        """
        Load a plugin definition and store the plugin in the manager.
        """
        assert not self.plugins.has_key(os.path.dirname(plugin_xml))
        log.debug('Loading definitions from %s' % plugin_xml)
        self.parser.parse(plugin_xml)
        plugin = self.loader.plugin
        plugin.path = os.path.dirname(plugin_xml)
        self.plugins[plugin.name] = plugin

    def load_plugins_from_dir(self, plugin_dir):
        log.debug('Loading plugins from %s' % plugin_dir)
        if not os.path.isdir(plugin_dir):
            return
        for plugin_xml in glob.glob(os.path.join(plugin_dir, '*', 'plugin.xml')):
            try:
                self.load_plugin(plugin_xml)
            except Exception, e:
                log.error('Could not load plugin definition %s' % plugin_xml, e)

    def get_plugins(self):
        return self.plugins.values()


# vim:sw=4:et
