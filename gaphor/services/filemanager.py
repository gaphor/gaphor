"""
The file service is responsible for loading and saving the user data.
"""

import gc
from zope import interface, component
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, build_action_group
from gaphor import UML


class FileManager(object):
    """
    The file service, responsible for loading and saving Gaphor models.
    """

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')
    gui_manager = inject('gui_manager')

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu action="file">
            <placeholder name="primary">
              <menuitem action="file-new" />
              <menuitem action="file-open" />
              <separator />
              <menuitem action="file-save" />
              <menuitem action="file-save-as" />
              <separator />
            </placeholder>
          </menu>
        </menubar>
      </ui>
    """
#              <menu name="recent" action="file-recent-files">
#              </menu>

    def __init__(self):
        self.filename = None

    def init(self, app):
        self.action_group = build_action_group(self)

    def shutdown(self):
        pass

    @action(name='file-new', stock_id='gtk-new')
    def new(self):
        element_factory = self.element_factory
        main_window = self.gui_manager.main_window
        if element_factory.size():
            dialog = gtk.MessageDialog(main_window.window,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO,
                _("Opening a new model will flush the currently loaded model.\nAny changes made will not be saved. Do you want to continue?"))
            answer = dialog.run()
            dialog.destroy()
            if answer != gtk.RESPONSE_YES:
                return

        element_factory.flush()
        gc.collect()
        model = element_factory.create(UML.Package)
        model.name = _('New model')
        diagram = element_factory.create(UML.Diagram)
        diagram.package = model
        diagram.name= _('main')
        self.filename = None
        element_factory.notify_model()

        main_window.select_element(diagram)
        main_window.show_diagram(diagram)

    @action(name='file-open', stock_id='gtk-open')
    def open(self):
        pass

    @action(name='file-save', stock_id='gtk-save')
    def save(self):
        pass

    @action(name='file-save-as', stock_id='gtk-save-as')
    def save_as(self):
        pass

    @action(name='file-recent-files', label=_('Recent files'), stock_id='gtk-recent')
    def recent_files(self):
        pass


#vim:sw=4:et:ai
