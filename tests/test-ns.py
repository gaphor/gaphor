# vim:sw=4:et
import gaphor.UML as UML
import pdb

# TODO:
# row_has_child_toggled() when no more ownedMembers

class NamespaceModel:
    """The NamespaceModel holds a view on the data model based on namespace
    relationships (such as a Package containing a Class)."""

    def __init__(self, model):
        self.root = self.new_node_from_element(model)

    def new_node_from_element(self, element):
        """Create a new node for an element. Owned members are also created."""
        node = (element, [])
        if isinstance(element, UML.Namespace):
            element.attach('ownedMember', self.on_ownedmember_changed, element)
            element.attach('name', self.on_name_changed, element)
            for om in element.ownedMember:
                node[1].append(self.new_node_from_element(om))
            self.sort_node(node)
        return node

    def detach_notifiers_from_node(self, node):
        """Detach notifiers for node"""
        node[0].detach('ownedMember', self.on_ownedmember_changed, node[0])
        node[0].detach('name', self.on_name_changed, node[0])
        for child in node[1]:
            self.detach_notifiers_from_node(child)

    def node_and_path_from_element(self, element):
        """Return (node, path) of an element."""
        assert isinstance(element, UML.NamedElement)
        if element.namespace:
            parent_node, parent_path = self.node_and_path_from_element(element.namespace)
            index = 0
            for child in parent_node[1]:
                if child[0] is element:
                    break;
                index += 1
            return child, parent_path + (index,)
        else:
            return self.root, ()

    def node_from_element(self, element):
        """Get the node for an element."""
        return self.node_and_path_from_element(element)[0]

    def path_from_element(self, element):
        """Get the path to an element as a tuple (e.g. (0, 1, 1))."""
        return self.node_and_path_from_element(element)[1]

    def node_from_path(self, path):
        """Get the node form a path."""
        try:
            node = self.root
            for index in path:
                node = node[1][index]
            return node
        except IndexError:
            print 'No path to node %s' % path

    def sort_node(self, node):
        """Sort nodes based on their names."""
        node[1].sort(lambda a, b: a[0].name == b[0].name and 0 or \
                                  a[0].name < b[0].name and -1 or 1)

    def dump(self):
        def doit(node, depth=0):
            print ' `' * depth, node[0].name
            for child in node[1]:
                doit(child, depth + 1)
        doit(self.root)

    def on_name_changed(self, name, element):
        """the name of element has changed, update the tree model"""
        path = self.path_from_element(element)
        if path:
            self.row_changed(path, self.get_iter(path))
            parent_node, parent_path = self.node_and_path_from_element(element.namespace)
            original = list(parent_node[1])
            #print 'original', original
            self.sort_node(parent_node)
            children = parent_node[1]
            #print 'original', original
            #print 'children', children
            if children != original:
                new_order = []
                for o in original:
                    new_order.append(children.index(o))
                #print 'new_order', new_order
                self.rows_reordered(parent_path, self.get_iter(parent_path), new_order)

    def on_ownedmember_changed(self, name, element):
        """update the tree model when the ownedMember list changes."""
        node = self.node_from_element(element)
        node_members = map(lambda e: e[0], node[1])
        owned_members = element.ownedMember
        if len(node[1]) < len(owned_members):
            # element added
            for om in owned_members:
                if om not in node_members:
                    # we have found the newly added element
                    node[1].append(self.new_node_from_element(om))
                    self.sort_node(node)
                    path = self.path_from_element(om)
                    self.row_inserted(path, self.get_iter(path))
                    assert len(node[1]) == len(owned_members)
                    break
        elif len(node[1]) > len(owned_members):
            # element removed
            for child in node[1]:
                if child[0] not in owned_members:
                    # we have found the removed element
                    path = self.path_from_element(child[0])
                    self.detach_notifiers_from_node(child)
                    node[1].remove(child)
                    self.row_deleted(path)
                    assert len(node[1]) == len(owned_members)
                    break
            if len(owned_members) == 0:
                path = self.path_from_element(element)
                self.row_has_child_toggled(path, self.get_iter(path))
        #else:
        #    print 'model is in sync'

    # TreeModel methods:

    def on_get_flags(self):
        """returns the GtkTreeModelFlags for this particular type of model"""
        return 0

    def on_get_n_columns(self):
        """returns the number of columns in the model"""
        return 1

    def on_get_column_type(self, index):
        """returns the type of a column in the model"""
        return gobject.TYPE_PYOBJECT

    def on_get_path (self, node):
        """returns the path for a node as a tuple (0, 1, 1)"""
        return self.path_from_element(node[0])

    def on_get_iter(self, path):
        """returns the node corresponding to the given path.
        The path is a tuple of values, like (0 1 1)."""
        return self.node_from_path(path)

    def on_get_value(self, node, column):
        """returns the model element that matches 'node'."""
        assert column == 0
        return node[0]

    def on_iter_next(self, node):
        """returns the next node at this level of the tree"""
        #print 'on_iter_next:', node, node.namespace
        try:
            parent = node_from_element(node[0].namespace)
            index = parent[1].index(node)
            return parent.ownedElement[index + 1]
        except IndexError:
            return None
        
    def on_iter_has_child(self, node):
        """returns true if this node has children"""
        #print 'on_iter_has_child', node
        return len(node[1]) > 0

    def on_iter_children(self, node):
        """returns the first child of this node"""
        #print 'on_iter_children'
        return node[1][0]

    def on_iter_n_children(self, node):
        """returns the number of children of this node"""
        #print 'on_iter_n_children'
        return len (node[1])

    def on_iter_nth_child(self, node, n):
        """returns the nth child of this node"""
        #print "on_iter_nth_child", node, n
        try:
            return node[1][n]
        except IndexError:
            return None

    def on_iter_parent(self, node):
        """returns the parent of this node"""
        #print "on_iter_parent", node
        return self.node_from_element(node[0].namespace)

if __name__ == '__main__':
    m = UML.Package()
    m.name = 'm'
    a = UML.Package()
    a.name = 'a'
    a.package = m
    b = UML.Package()
    b.name = 'b'
    b.package = a
    c = UML.Class()
    c.name = 'c'
    c.package = b
    d = UML.Class()
    d.name = 'd'
    d.package = a
    e = UML.Class()
    e.name = 'e'
    e.package = b

    print 'm', m
    print 'a', a
    print 'b', b
    print 'c', c
    print 'd', d
    print 'e', e

    ns = NamespaceModel(m)

    print 'a', ns.path_from_element(a)
    print 'b', ns.path_from_element(b)
    print 'c', ns.path_from_element(c)
    print 'd', ns.path_from_element(d)
    print 'e', ns.path_from_element(e)

    print a, ns.node_from_path(ns.path_from_element(a))
    print b, ns.node_from_path(ns.path_from_element(b))
    print c, ns.node_from_path(ns.path_from_element(c))
    print d, ns.node_from_path(ns.path_from_element(d))
    print e, ns.node_from_path(ns.path_from_element(e))

    print '---'
    ns.dump()
    print '---'
    del b.ownedClassifier[c]
    ns.dump()
    print '---'
    c.package = a
    ns.dump()
    print '---'
    #del a.ownedClassifier[b]
    b.package = m
    ns.dump()
    print '---'
    d.name = 'aa'
    ns.dump()
