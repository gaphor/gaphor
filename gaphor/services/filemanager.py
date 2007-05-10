"""
The file service is responsible for loading and saving the user data.
"""

from zope import interface, component
from gaphor.interfaces import IService, IActionProvider
from gaphor.core import _, inject, action, build_action_group

class FileManager(object):
    """
    The file service, responsible for loading and saving Gaphor models.
    """

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')

    menu_xml = """
      <ui>
        <menubar name="mainwindow">
          <menu name="file">
	    <placeholder name="primary">
              <menuitem action="file-new" />
              <menuitem action="file-open" />
              <menu name="recent" action="file-recent-files">
	      </menu>
              <separator />
              <menuitem action="file-save" />
              <menuitem action="file-save-as" />
              <separator />
	    </placeholder>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        pass

    def init(self, app):
        self.action_group = build_action_group(self)

    @action(name='file-new', stock_id='gtk-new')
    def new(self):
        pass

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
