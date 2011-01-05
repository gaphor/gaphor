"""
"""

import pkg_resources
from zope import interface

from gaphor.misc.logger import Logger
from gaphor.interfaces import IService, IActionProvider
from gaphor.ui.interfaces import IUIComponent
from gaphor.core import inject

class GUIManager(object):

    interface.implements(IService)

    action_manager = inject('action_manager')
    logger = Logger(name='GUIMANAGER')

    def __init__(self):
        self._ui_components = dict()

    main_window = property(lambda s: s._main_window)

    def init(self, app):
        #self.init_pygtk()
        self.init_stock_icons()
        self.init_ui_components()
        self.init_main_window()

    def init_pygtk(self):
        """
        Make sure we have GTK+ >= 2.0
        """
        import pygtk
        pygtk.require('2.0')
        del pygtk

    def init_stock_icons(self):
        
        self.logger.info('Initializing stock icons')
        
        # Load stock items
        import gaphor.ui.stock
        gaphor.ui.stock.load_stock_icons()

    def init_ui_components(self):
        
        self.logger.info('Initializing components')
        
        ui_manager = self.action_manager.ui_manager
        
        for ep in pkg_resources.iter_entry_points('gaphor.uicomponents'):
            
            self.logger.debug('UI component is %s' % ep.name)
            
            cls = ep.load()
            
            if not IUIComponent.implementedBy(cls):
                raise 'MisConfigurationException', 'Entry point %s doesn''t provide IUIComponent' % ep.name
                
            uicomp = cls()
            uicomp.ui_manager = ui_manager
            self._ui_components[ep.name] = uicomp
            
            if IActionProvider.providedBy(uicomp):
                self.action_manager.register_action_provider(uicomp)
                
    def init_main_window(self):
        
        self.logger.info('Initializing main window')
        
        from gaphor.ui.accelmap import load_accel_map

        load_accel_map()
        self._main_window = self._ui_components['mainwindow']
        self._main_window.construct()

    def shutdown(self):
        
        self.logger.info('Shutting down')
        
        if self._main_window.window:
            self._main_window.window.destroy()
        from gaphor.ui.accelmap import save_accel_map
        save_accel_map()

# vim:sw=4:et:ai
