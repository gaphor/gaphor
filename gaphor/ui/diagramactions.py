"""
Commands related to the Diagram (DiaCanvas)
"""
# vim: sw=4

import gtk
import diacanvas
import gaphor
import gaphor.UML as UML
from gaphor.undomanager import UndoTransactionAspect, weave_method
from gaphor.misc.action import Action, CheckAction, RadioAction
from gaphor.misc.action import register_action as _register_action
from gaphor.misc.action import action_dependencies as _action_dependencies

def register_action(action, *args):
    _register_action(action, *args)
    _action_dependencies(action, 'TabChange')

class CloseTabAction(Action):
    id = 'FileCloseTab'
    stock_id = 'gtk-close'
    tooltip='Close the diagram window'

    def init(self, window):
        self._window = window

    def update(self):
        self.sensitive = self._window.get_current_diagram_tab() is not None

    def execute(self):
        window = self._window.get_current_diagram_tab()
        window.close()

register_action(CloseTabAction)


class UndoStackAction(Action):
    """Dummy action that triggers the undo and redo actions to update
    themselves.
    """
    id = 'EditUndoStack'
    
    def init(self, window):
        pass

register_action(UndoStackAction)

class UndoAction(Action):
    id = 'EditUndo'
    stock_id = 'gtk-undo'
    label = '_Undo'
    tooltip = 'Undo the most recent changes'
    accel = 'C-z'

    # TODO: check if the diagram can undo.

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = diagram_tab and diagram_tab.get_canvas().undo_manager.can_undo()

    def execute(self):
        self._window.get_current_diagram_view().canvas.undo_manager.undo_transaction()
        self.update()
        self._window.execute_action('EditUndoStack')

register_action(UndoAction, 'EditUndoStack')


class RedoAction(Action):
    id = 'EditRedo'
    stock_id = 'gtk-redo'
    tooltip = 'Redo the undone changes'
    accel = 'C-r'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = diagram_tab and diagram_tab.get_canvas().undo_manager.can_redo()

    def execute(self):
        self._window.get_current_diagram_view().canvas.undo_manager.redo_transaction()
        self.update()
        self._window.execute_action('EditUndoStack')

register_action(RedoAction, 'EditUndoStack')

class ToolChangeAction(Action):
    """Dummy, triggered when a new tool is selected.
    """
    id = 'ToolChange'

    def init(self, window):
        pass

register_action(ToolChangeAction)


class SelectAction(Action):
    """Dummy action that is "called" when the selected items on the canvas
    change.
    """
    id = 'ItemSelect'

    def init(self, window):
        pass

register_action(SelectAction)


class FocusAction(Action):
    """Dummy action that is "called" when the selected items on the canvas
    change.
    """
    id = 'ItemFocus'

    def init(self, window):
        pass

register_action(FocusAction)


class DiagramDropAction(Action):
    """Dummy action that is "called" when a new item is placed on the canvas
    by means of Drag-and-drop.
    """
    id = 'ItemDiagramDrop'

    def init(self, window):
        self._window = window
 
    def execute(self):
	self._window.execute_action('CreateLinks')

register_action(DiagramDropAction)


class SelectAllAction(Action):
    id = 'EditSelectAll'
    label = '_Select all'
    accel = 'C-a'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = bool(diagram_tab)

    def execute(self):
        self._window.get_current_diagram_view().select_all()

register_action(SelectAllAction)


class DeselectAllAction(Action):
    id = 'EditDeselectAll'
    label = 'Des_elect all'
    accel = 'C-S-a'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = diagram_tab and len(diagram_tab.get_view().selected_items) > 0

    def execute(self):
        self._window.get_current_diagram_view().unselect_all()

register_action(DeselectAllAction, 'ItemSelect', 'EditDelete')


class DeleteAction(Action):
    """Delete each selected canvas item.
    """
    id = 'EditDelete'
    label = '_Delete'
    accel = 'C-d'
    stock_id = 'gtk-delete'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = diagram_tab and len(diagram_tab.get_view().selected_items) > 0

    def execute(self):
        view = self._window.get_current_diagram_view()
        # Confirm deletion of last views to model objects
        # They will be deleted along with their last view
        if not self.mayRemoveFromModal(view):
            return

        if view.is_focus():
            view.canvas.undo_manager.begin_transaction()
            try:
                items = view.selected_items
                for i in items:
                    i.item.unlink()
            finally:
                view.canvas.undo_manager.commit_transaction()
    
    def mayRemoveFromModal(self, view):
        ''' Check if there are items which will be deleted from the model (when their last views are deleted). If so request user confirmation before deletion. '''
        items = view.selected_items
        for i in items:
            if self.isLastView(i):
                return self.requestConfirmation()
        return True

    def isLastView(self, item):
        ''' Check if the current view is the last view to its object '''
        if item.item.subject and len(item.item.subject.presentation)==1:
            return True
        return False

    def requestConfirmation(self):
        ''' Request user confirmation on deleting the item from the model '''
        dialog = gtk.MessageDialog(
                None,
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                gtk.MESSAGE_WARNING,
                gtk.BUTTONS_YES_NO,
                'This will remove the selected items from the model. Are you sure?'
                )
        dialog.set_transient_for(self._window.window)
        value = dialog.run()
        dialog.destroy()
        if value==gtk.RESPONSE_YES:
            return True
        return False


register_action(DeleteAction, 'ItemSelect')


class CopyAction(Action):
    """Copy/Cut/Paste functionality required a lot of thinking:

    Store a list of DiagramItems that have to be copied in resource
    'copy-buffer'.

      - in order to make copy/paste work, the load/save functions should be
        generatlised to allow a subset to be saved/loaded (which is needed
        anyway for exporting/importing stereotype Profiles).
      - How many data should be saved? (e.g. we copy a diagram item, remove it
        (the underlaying UML element is removed) and the paste the copied item.
        The diagram should act as if we have placed a copy of the removed item
        on the canvas and make the uml element visible again.
    """
    id = 'EditCopy'
    label = '_Copy'
    accel = 'C-c'
    stock_id = 'gtk-copy'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = diagram_tab and len(diagram_tab.get_view().selected_items) > 0

    def execute(self):
        view = self._window.get_current_diagram_view()
        if view.is_focus():
            items = view.selected_items
            copy_items = []
            for i in items:
                copy_items.append(i.item)
                #i.item.save(save_func)
            if copy_items:
                gaphor.resource.set('copy-buffer', copy_items)
        tab = self._window.get_current_diagram_tab()

register_action(CopyAction, 'ItemFocus')


class PasteAction(Action):
    """Copy/Cut/Paste functionality required a lot of thinking:

    Create a copy of DiagramItems that have to be copied in resource
    'copy-buffer'.

      - in order to make copy/paste work, the load/save functions should be
        generatlised to allow a subset to be saved/loaded (which is needed
        anyway for exporting/importing stereotype Profiles).
      - How many data should be saved? (e.g. we copy a diagram item, remove it
        (the underlaying UML element is removed) and the paste the copied item.
        The diagram should act as if we have placed a copy of the removed item
        on the canvas and make the uml element visible again.
    """
    id = 'EditPaste'
    label = '_Paste'
    accel = 'C-v'
    stock_id = 'gtk-paste'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = diagram_tab and gaphor.resource('copy-buffer', [])

    def _load_element(self, name, value):
        """Copy an element, preferbly from the list of new items,
        otherwise from the elementFactory.
        If it does not exist there, do not copy it!
        """
        item = self._new_items.get(value.id)
        if item:
            self._item.load(name, item)
        else:
            item = self._factory.lookup(value.id)
            if item:
                self._item.load(name, item)

    def copy_func(self, name, value, reference=False):
        if reference or isinstance(value, UML.Element):
            self._load_element(name, value)
        elif isinstance(value, gaphor.UML.collection):
            for item in value:
                self._load_element(name, item)
        elif isinstance(value, diacanvas.CanvasItem):
            self._load_element(name, value)
        else:
            # Plain attribute
            self._item.load(name, str(value))

    def execute(self):
        view = self._window.get_current_diagram_view()
        if not view:
            return

        diagram = view.get_diagram()
        canvas = diagram.canvas
        if not canvas:
            return

        copy_items = [ c for c in gaphor.resource('copy-buffer', []) if c.canvas ]

        # Mapping original id -> new item
        self._new_items = {}
        self._factory = gaphor.resource('ElementFactory')

        # Create new id's that have to be used to create the items:
        for ci in copy_items:
            self._new_items[ci.id] = diagram.create(type(ci))
            #self._new_items[ci.id].set_property('canvas', canvas)

        # Copy attributes and references. References should be
        #  1. in the ElementFactory (hence they are model elements)
        #  2. refered to in new_items
        #  3. canvas property is overridden
        for ci in copy_items:
            self._item = self._new_items[ci.id]
            ci.save(self.copy_func)

        for item in self._new_items.values():
            item.move(10, 10)

        for item in self._new_items.values():
            item.postload()

        view.unselect_all()

        for item in self._new_items.values():
            view.select(view.find_view_item(item))

weave_method(PasteAction.execute, UndoTransactionAspect)
register_action(PasteAction, 'EditCopy')


class ZoomInAction(Action):
    id = 'ViewZoomIn'
    label = 'Zoom _In'
    accel = 'C-+'
    stock_id = 'gtk-zoom-in'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = bool(diagram_tab)

    def execute(self):
        view = self._window.get_current_diagram_view()
        view.set_zoom(view.get_zoom() + 0.1)

register_action(ZoomInAction)


class ZoomOutAction(Action):
    id = 'ViewZoomOut'
    label = 'Zoom _Out'
    accel = 'C--'
    stock_id = 'gtk-zoom-out'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = bool(diagram_tab)

    def execute(self):
        view = self._window.get_current_diagram_view()
        view.set_zoom(view.get_zoom() - 0.1)

register_action(ZoomOutAction)


class Zoom100Action(Action):
    id = 'ViewZoom100'
    label = '_Zoom 100%'
    stock_id = 'gtk-zoom-100'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = bool(diagram_tab)

    def execute(self):
        self._window.get_current_diagram_view().set_zoom(1.0)

register_action(Zoom100Action)


class SnapToGridAction(CheckAction):
    id = 'SnapToGrid'
    label = '_Snap to grid'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = bool(diagram_tab)
        self.active = diagram_tab and diagram_tab.get_canvas().get_property('snap_to_grid')

    def execute(self):
        diagram_tab = self._window.get_current_diagram_tab()
        diagram_tab.get_canvas().set_property('snap_to_grid', self.active)

register_action(SnapToGridAction)

class ShowGridAction(CheckAction):
    id = 'ShowGrid'
    label = 'S_how grid'

    def init(self, window):
        self._window = window

    def update(self):
        diagram_tab = self._window.get_current_diagram_tab()
        self.sensitive = bool(diagram_tab)
        self.active = diagram_tab and diagram_tab.get_canvas().get_property('grid_color') != diagram_tab.get_canvas().get_property('grid_bg') 

    def execute(self):
        tab = self._window.get_current_diagram_tab()
        if tab:
            canvas = tab.get_canvas()
            canvas.set_property('grid_color', self.active and 255 or canvas.get_property('grid_bg'))

register_action(ShowGridAction)

