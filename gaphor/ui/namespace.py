# vim: sw=4:et:ai
"""This is the TreeView that is most common (for example: it is used
in Rational Rose). This is a tree based on namespace relationships. As
a result only classifiers are shown here.
"""

import gobject
import gtk
import stock

import gaphor.UML as UML
from gaphor import resource
from gaphor.undomanager import get_undo_manager
import operator

# The following items will not be shown in the treeview, although they
# are UML.Namespace elements.
_default_exclude_list = ( UML.Parameter, UML.Association )

class NamespaceModel(gtk.GenericTreeModel):
    """The NamespaceModel holds a view on the data model based on namespace
    relationships (such as a Package containing a Class).

    NamedElement.namespace[1] -- Namespace.ownedMember[*]
    """

    def __init__(self, factory):
        if not isinstance (factory, UML.ElementFactory):
            raise AttributeError, 'factory should be a %s' % UML.ElementFactory.__name__
        # Init parent:
        #self.__gobject_init__()
        gtk.GenericTreeModel.__init__(self)

        # We own the references to the iterators.
        self.set_property ('leak_references', 0)

        self.factory = factory

        factory.connect(self.on_factory_signals)

        self.root = (None, [])

        self.exclude = _default_exclude_list

    def new_node_from_element(self, element, parent_node):
        """Create a new node for an element. Owned members are also created."""
        if isinstance(element, self.exclude):
            return
        node = (element, [])
        parent_node[1].append(node)
        # Sort the nodes, so we can tell the views exactly where the element
        # is inserted.
        self.sort_node(parent_node)
        path = self.path_from_element(element)
        #print 'new_node_from_element', path, element, element.name
        self.row_inserted(path, self.get_iter(path))
        element.connect('name', self.on_name_changed)

        if isinstance(element, UML.Namespace):
            element.connect('ownedMember', self.on_ownedmember_changed)
            for om in list(element.ownedMember):
                self.new_node_from_element(om, node)
        return node

    def detach_notifiers_from_node(self, node):
        """Detach notifiers for node
        """
        node[0].disconnect(self.on_name_changed)
        if isinstance(node[0], UML.Namespace):
            node[0].disconnect(self.on_ownedmember_changed)
            for child in node[1]:
                self.detach_notifiers_from_node(child)

    def node_and_path_from_element(self, element):
        """Return (node, path) of an element.
        """
        #assert isinstance(element, UML.NamedElement)
        if element:
            parent_node, parent_path = self.node_and_path_from_element(element.namespace)
            index = 0
            for child in parent_node[1]:
                if child[0] is element:
                    break;
                index += 1
            else:
                raise AttributeError, 'Element %s is not part of the NamespaceModel' % element
            #print 'parent_path', parent_node[1], parent_path + (index,)
            return child, parent_path + (index,)
        else:
            return self.root, ()

    def node_from_element(self, element):
        """Get the node for an element.
        """
        return self.node_and_path_from_element(element)[0]

    def path_from_element(self, element):
        """Get the path to an element as a tuple (e.g. (0, 1, 1)).
        """
        return self.node_and_path_from_element(element)[1]

    def node_from_path(self, path):
        """Get the node form a path. None is returned if no node is found.
        """
        try:
            node = self.root
            for index in path:
                node = node[1][index]
            return node
        except IndexError:
            return None
        #    print 'No path to node %s' % path

    def element_from_node(self, node):
        return node[0]

    def element_from_path(self, path):
        return self.node_from_path(path)[0]

    def __sort_node(a, b):
        m = a[0]
        n = b[0]
        if type(m) is type(n):
            if m.name == n.name:
                return 0
            elif m.name < n.name:
                return -1
            else:
                return 1
        if isinstance(m, UML.Diagram):
            return -1
        elif isinstance(n, UML.Diagram):
            return 1

    def sort_node(self, node):
        """Sort nodes based on their names.
        If path is set, the rows are "reordered".
        """
        # Do something like this (only a bit faster):
        #    node[1].sort(lambda a, b: a[0].name == b[0].name and 0 or \
        #                              a[0].name < b[0].name and -1 or 1)
        # Uses Python cookbook recipe 2.6
        children = node[1]
        length = len(children)
        getitem = operator.getitem
        # Create a list of tuples (name, current index, node)
        intermed = map(None,
                       map(getattr, 
                           map(getitem, children, (0,) * length),
                           ('name',) * length), # name
                       xrange(length), # index
                       children) # node
        intermed.sort()
        # Replace the current node list with the new sorted list.
        node[1][:] = map(getitem, intermed, (-1,) * length)

    def dump(self):
        def doit(node, depth=0):
            if node[0]:
                print ' `' * depth, node[0].name, self.path_from_element(node[0])
            else:
                print ' `' * depth, '<None>'
            for child in node[1]:
                doit(child, depth + 1)
        doit(self.root)

    def on_name_changed(self, element, pspec):
        """the name of element has changed, update the tree model
        """
        path = self.path_from_element(element)
        if path:
            self.row_changed(path, self.get_iter(path))
            parent_node, parent_path = self.node_and_path_from_element(element.namespace)
            original = list(parent_node[1])
            self.sort_node(parent_node)
            children = parent_node[1]
            if children != original and hasattr(self, 'rows_reordered'):
                # reorder the list:
                self.rows_reordered(parent_path, self.get_iter(parent_path),
                                    map(list.index,
                                        [original] * len(children), children))

    def on_ownedmember_changed(self, element, pspec):
        """update the tree model when the ownedMember list changes.
        Element is the object whose ownedMember property has changed.
        """
        node = self.node_from_element(element)
        # The elements currently known by the tree model
        node_members = map(lambda e: e[0], node[1])
        # The elements that are now children of the element
        owned_members = filter(lambda e: not isinstance(e, self.exclude), element.ownedMember)
        #owned_members = element.ownedMember
        if len(node_members) < len(owned_members):
            # element added
            #print 'NamespaceModel: element added'
            for om in owned_members:
                if om not in node_members:
                    # we have found the newly added element
                    self.new_node_from_element(om, node)
                    assert len(node[1]) == len(owned_members)
                    break
        elif len(node_members) > len(owned_members):
            # element removed
            #print 'element removed', element.name, element.namespace, node
            index = 0
            for child in node[1]:
                if child[0] not in owned_members:
                    # we have found the removed element
                    #path = self.path_from_element(child[0])
                    path = self.path_from_element(element) + (index,)
                    #log.debug('NS: removing node "%s" from "%s" (path=%s)' % (child[0].name, element.name, path))
                    #print 'path=', child[0].name, path
                    try:
                        self.detach_notifiers_from_node(child)
                        node[1].remove(child)
                        self.row_deleted(path)
                        assert len(node[1]) == len(owned_members)
                    except Exception, e:
                        log.warning('error:', e)
                    break
                index += 1
            if len(owned_members) == 0:
                path = self.path_from_element(element)
                self.row_has_child_toggled(path, self.get_iter(path))
        #else:
            #log.debug('model is in sync for "%s"' % element.name)

    def flush(self):
        for i in self.root[1]:
            self.detach_notifiers_from_node(i)
            # remove the node, it is now the first in the list:
            self.row_deleted((0,))
        self.root = (None, [])

    def _build_model(self):
        toplevel = self.factory.select(lambda e: isinstance(e, UML.Namespace) and not e.namespace)

        for t in toplevel:
            #print 'factory::model toplevel', t, t.name
            self.new_node_from_element(t, self.root)
        #print 'self.root', self.root

    def refresh(self):
        self.flush()
        self._build_model()

    def on_factory_signals (self, obj, pspec):
        if pspec == 'model':
            self._build_model()
        elif pspec == 'flush':
            self.flush()

        # TODO: add create (and remove?) signal so we can add 
        #elif pspec == 'create':
        #    self.new_node_from_element(obj, self.root)

    # TreeModel methods:

    def on_get_flags(self):
        """Returns the GtkTreeModelFlags for this particular type of model.
        """
        return 0

    def on_get_n_columns(self):
        """Returns the number of columns in the model.
        """
        return 1

    def on_get_column_type(self, index):
        """Returns the type of a column in the model.
        """
        return gobject.TYPE_PYOBJECT

    def on_get_path (self, node):
        """Returns the path for a node as a tuple (0, 1, 1).
        """
        #print 'on_get_path', node
        return self.path_from_element(node[0])

    def on_get_iter(self, path):
        """Returns the node corresponding to the given path.
        The path is a tuple of values, like (0 1 1). Returns None if no
        iterator can be created.
        """
        #print 'on_get_iter', path
        return self.node_from_path(path)

    def on_get_value(self, node, column):
        """Returns the model element that matches 'node'.
        """
        assert column == 0, 'column can only be 0'
        #print 'on_get_value', node, column
        return node[0]

    def on_iter_next(self, node):
        """Returns the next node at this level of the tree (None if no
        next element).
        """
        #print 'on_iter_next:', node
        try:
            parent = self.node_from_element(node[0].namespace)
            #print 'on_iter_next: parent', parent
            index = parent[1].index(node)
            return parent[1][index + 1]
        except IndexError, e:
            #print 'error: on_next_iter', e, parent
            #import traceback
            #traceback.print_exc()
            return None
        
    def on_iter_has_child(self, node):
        """Returns true if this node has children, or None.
        """
        #print 'on_iter_has_child', node
        return len(node[1]) > 0

    def on_iter_children(self, node):
        """Returns the first child of this node, or None.
        """
        #print 'on_iter_children'
        return node[1][0]

    def on_iter_n_children(self, node):
        """Returns the number of children of this node.
        """
        #print 'on_iter_n_children'
        return len (node[1])

    def on_iter_nth_child(self, node, n):
        """Returns the nth child of this node.
        """
        #print "on_iter_nth_child", node, n
        try:
            if node is None:
                node = self.root
            return node[1][n]
        except TypeError, e:
            #print e, node, n
            #import traceback
            #traceback.print_exc()
            return None

    def on_iter_parent(self, node):
        """Returns the parent of this node or None if no parent"""
        #print "on_iter_parent", node
        return self.node_from_element(node[0].namespace)

class NamespaceView(gtk.TreeView):

    TARGET_STRING = 0
    TARGET_ELEMENT_ID = 1
    DND_TARGETS = [
        ('STRING', 0, TARGET_STRING),
        ('text/plain', 0, TARGET_STRING),
        ('gaphor/element-id', 0, TARGET_ELEMENT_ID)]
    # Can not set signals for some reason...
    #__gsignals__ = { 'drag-drop': 'override',
    #                 'drag-data-get': 'override',
    #                 'drag-data-delete': 'override',
    #                 'drag-data-received': 'override' }

    def __init__(self, model):
        assert isinstance (model, NamespaceModel), 'model is not a NamespaceModel (%s)' % str(model)
        self.__gobject_init__()
        gtk.TreeView.__init__(self, model)
        self.icon_cache = {}

        self.set_property('headers-visible', 0)
        self.set_rules_hint(gtk.TRUE)
        selection = self.get_selection()
        selection.set_mode(gtk.SELECTION_BROWSE)
        column = gtk.TreeViewColumn ('')
        # First cell in the column is for an image...
        cell = gtk.CellRendererPixbuf ()
        column.pack_start (cell, 0)
        column.set_cell_data_func (cell, self._set_pixbuf, None)
        
        # Second cell if for the name of the object...
        cell = gtk.CellRendererText ()
        #cell.set_property ('editable', 1)
        cell.connect('edited', self._name_edited)
        column.pack_start (cell, 0)
        column.set_cell_data_func (cell, self._set_name, None)

        assert len (column.get_cell_renderers()) == 2
        self.append_column (column)

        # DND info:
        # drag
        self.enable_model_drag_source(gtk.gdk.BUTTON1_MASK,
                             [NamespaceView.DND_TARGETS[-1]],
                             gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
        self.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON3_MASK,
                             NamespaceView.DND_TARGETS,
                             gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_LINK)
        self.connect('drag-data-get', NamespaceView.on_drag_data_get)

        # drop
        #self.drag_dest_set (gtk.DEST_DEFAULT_ALL, [NamespaceView.DND_TARGETS[-1]],
        #                    gtk.gdk.ACTION_DEFAULT)
        self.enable_model_drag_dest([NamespaceView.DND_TARGETS[-1]],
                                    gtk.gdk.ACTION_DEFAULT)
        self.connect('drag-data-received', NamespaceView.on_drag_data_received)
        self.connect('drag-drop', NamespaceView.on_drag_drop)
        self.connect('drag-data-delete', NamespaceView.on_drag_data_delete)

    def get_selected_element(self):
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if not iter:
            return
        return model.get_value(iter, 0)

    def _set_pixbuf (self, column, cell, model, iter, data):
        value = model.get_value(iter, 0)
        try:
            icon = self.icon_cache[type(value)]
        except KeyError:
            stock_id = stock.get_stock_id(type(value))
            if stock_id:
                icon = self.render_icon(stock_id, gtk.ICON_SIZE_MENU, '')
            else:
                icon = None
            self.icon_cache[type(value)] = icon
        cell.set_property('pixbuf', icon)

    def _set_name (self, column, cell, model, iter, data):
        value = model.get_value(iter, 0)
        #print 'set_name:', value
        name = value and (value.name or '').replace('\n', ' ') or '<None>'
        cell.set_property('text', name)

    def _name_edited(self, cell, path_str, new_text):
        """The text has been edited. This method updates the data object.
        Note that 'path_str' is a string where the fields are separated by
        colons ':', like this: '0:1:1'. We first turn them into a tuple.
        """
        try:
            model = self.get_property('model')
            iter = model.get_iter_from_string(path_str)
            element = model.get_value(iter, 0)
            element.name = new_text
        except Exception, e:
            log.error('Could not create path from string "%s"' % path_str)

#    def do_drag_begin (self, context):
#        print 'do_drag_begin'

    def on_drag_data_get(self, context, selection_data, info, time):
        """Get the data to be dropped by on_drag_data_received().
        We send the id of the dragged element.
        """
        #log.debug('on_drag_data_get')
        selection = self.get_selection()
        model, iter = selection.get_selected()
        if iter:
            element = model.get_value(iter, 0)
            if info == NamespaceView.TARGET_ELEMENT_ID:
                selection_data.set(selection_data.target, 8, str(element.id))
            else:
                selection_data.set(selection_data.target, 8, element.name)

    def on_drag_data_delete (self, context):
        """DnD magic. do not touch
        """
        self.emit_stop_by_name('drag-data-delete')

    # Drop
    def on_drag_data_received(self, context, x, y, selection, info, time):
        """Drop the data send by on_drag_data_get().
        """
        self.emit_stop_by_name('drag-data-received')
        #print 'drag_data_received'
        data = selection.data
        drop_info = self.get_dest_row_at_pos(x, y)
        if drop_info:
            #print 'drop_info', drop_info
            model = self.get_model()
            factory = resource(UML.ElementFactory)
            element = factory.lookup(data)
            path, position = drop_info
            iter = model.get_iter(path)
            dest_element = model.get_value(iter, 0)
            assert dest_element
            # Add the item to the parent if it is dropped on the same level,
            # else add it to the item.
            if position in (gtk.TREE_VIEW_DROP_BEFORE, gtk.TREE_VIEW_DROP_AFTER):
                parent_iter = model.iter_parent(iter)
                dest_element = model.get_value(parent_iter, 0)
            #print element.name, dest_element.name
            try:
                # Check if element is part of the namespace of dest_element:
                ns = dest_element
                while ns:
                    if ns is element:
                        raise AttributeError
                    ns = ns.namespace

                # Set package. This only works for classifiers, packages and
                # diagrams. Properties and operations should not be moved.
                get_undo_manager().begin_transaction()
                element.package = dest_element
                get_undo_manager().commit_transaction()

            except AttributeError:
                #print dir(context)
                context.drop_finish(gtk.FALSE, time)
            else:
                context.drop_finish(gtk.TRUE, time)
                # Finally let's try to select the element again.
                path = model.path_from_element(element)
                self.expand_row(path[:-1], False)
                selection = self.get_selection()
                selection.select_path(path)

    def on_drag_drop(self, context, x, y, time):
        """DnD magic. do not touch
        """
        self.emit_stop_by_name('drag-drop')
        #print 'drag_drop',context,x,y,time
        self.drag_get_data(context, context.targets[-1], time)
        return 1

gobject.type_register(NamespaceModel)
gobject.type_register(NamespaceView)

#if __debug__:
#    from gaphor.misc.aspects import weave_method, TimerAspect
#    NamespaceModel.sort_node = weave_method(NamespaceModel.sort_node, TimerAspect)
