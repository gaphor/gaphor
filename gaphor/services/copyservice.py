"""
Copy / Paste functionality
"""

from zope import interface, component
import gaphas
from gaphor import UML
from gaphor.interfaces import IService, IActionProvider
from gaphor.ui.interfaces import IDiagramSelectionChange
from gaphor.core import _, inject, action, build_action_group, transactional


class CopyService(object):
    """
    Copy/Cut/Paste functionality required a lot of thinking:

    Store a list of DiagramItems that have to be copied in a global
    'copy-buffer'.

    - in order to make copy/paste work, the load/save functions should be
      generatlised to allow a subset to be saved/loaded (which is needed
      anyway for exporting/importing stereotype Profiles).
    - How many data should be saved? (e.g. we copy a diagram item, remove it
      (the underlaying UML element is removed) and the paste the copied item.
      The diagram should act as if we have placed a copy of the removed item
      on the canvas and make the uml element visible again.
    """

    interface.implements(IService, IActionProvider)

    element_factory = inject('element_factory')
    gui_manager = inject('gui_manager')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="edit">
            <placeholder name="primary">
              <menuitem action="edit-copy" />
              <menuitem action="edit-paste" />
            </placeholder>
          </menu>
        </menubar>
      </ui>
    """

    def __init__(self):
        self.copy_buffer = set()
        self.action_group = build_action_group(self)

    def init(self, app):
        self._app = app
        self.action_group.get_action('edit-copy').props.sensitive = False
        self.action_group.get_action('edit-paste').props.sensitive = False
        
        app.registerHandler(self._update)

    def shutdown(self):
        self.copy_buffer = set()
        self._app.unregisterHandler(self._update)

    @component.adapter(IDiagramSelectionChange)
    def _update(self, event):
        diagram_view = event.diagram_view
        self.action_group.get_action('edit-copy').props.sensitive = bool(diagram_view.selected_items)

    def copy(self, items):
        if items:
            self.copy_buffer = set(items)
            self.action_group.get_action('edit-paste').props.sensitive = True

    def _load_element(self, name, value):
        """
        Copy an element, preferbly from the list of new items,
        otherwise from the element factory.
        If it does not exist there, do not copy it!
        """
        item = self._new_items.get(value.id)
        if item:
            self._item.load(name, item)
        else:
            item = self.element_factory.lookup(value.id)
            if item:
                self._item.load(name, item)

    def copy_func(self, name, value, reference=False):
        if reference or isinstance(value, UML.Element):
            self._load_element(name, value)
        elif isinstance(value, UML.collection):
            for item in value:
                self._load_element(name, item)
        elif isinstance(value, gaphas.Item):
            self._load_element(name, value)
        else:
            # Plain attribute
            self._item.load(name, str(value))

    @transactional
    def paste(self, diagram):
        """
        Paste items in the copy-buffer to the diagram
        """
        canvas = diagram.canvas
        if not canvas:
            return

        copy_items = [ c for c in self.copy_buffer if c.canvas ]

        # Mapping original id -> new item
        self._new_items = {}

        # Create new id's that have to be used to create the items:
        for ci in copy_items:
            self._new_items[ci.id] = diagram.create(type(ci))

        # Copy attributes and references. References should be
        #  1. in the ElementFactory (hence they are model elements)
        #  2. refered to in new_items
        #  3. canvas property is overridden
        for ci in copy_items:
            self._item = self._new_items[ci.id]
            ci.save(self.copy_func)

        for item in self._new_items.values():
            item.matrix.translate(10, 10)

        for item in self._new_items.values():
            item.postload()


    @action(name='edit-copy', stock_id='gtk-copy')
    def _copy(self):
        view = self.gui_manager.main_window.get_current_diagram_view()
        if view.is_focus():
            items = view.selected_items
            copy_items = []
            for i in items:
                copy_items.append(i)
            self.copy(copy_items)

    @action(name='edit-paste', stock_id='gtk-paste')
    def paste_action(self):
        view = self.gui_manager.main_window.get_current_diagram_view()
        diagram = self.gui_manager.main_window.get_current_diagram()
        if not view:
            return

        self.paste(diagram)

        view.unselect_all()

        for item in self._new_items.values():
            view.select_item(item)


# vim:sw=4:et:ai
