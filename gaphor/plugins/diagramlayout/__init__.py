"""
This module provides a means to automatocally layout diagrams.

The layout is done like this:
 - First all nodes (Classes, packages, comments) on a digram are determined
 - A vertical ordering is determined based on the inheritance
 - A horizontal ordering is determined based on associations and dependencies
 - The nodes are moved to their place
 - Lines are reconnected to the nodes, so everything looks pretty.
"""
from __future__ import division

from past.utils import old_div
import random

from zope import interface

from gaphor.core import inject, action, build_action_group, transactional
from gaphor.diagram import items
from gaphor.interfaces import IService, IActionProvider
from gaphor.plugins.diagramlayout import toposort


class DiagramLayout(object):

    interface.implements(IService, IActionProvider)

    main_window = inject('main_window')

    menu_xml = """
      <ui>
        <menubar action="mainwindow">
          <menu action="diagram">
            <menuitem action="diagram-layout" />
          </menu>
        </menubar>
      </ui>"""

    def __init__(self):
        self.action_group = build_action_group(self)

    def init(self, app):
        pass

    def shutdown(self):
        pass

    def update(self):
        self.sensitive = bool(self.get_window().get_current_diagram())

    @action(name='diagram-layout', label='Layout diagram',
            tooltip='simple diagram layout')
    def execute(self):
        d = self.main_window.get_current_diagram()
        self.layout_diagram(d)

    @transactional
    def layout_diagram(self, diag):
        layout_diagram(diag)


MARGIN = 100

def layout_diagram(diag):
    """
    So an attempt to layout (order) the items on a diagram. The items
    should already be placed on the diagram and the items should already be
    connected.

    This function works on the diagram items (hence it does not check relations
    in the datamodel, only the ones drawn on the diagram) to produce a
    decent layout.
    """
    nodes = []
    primary_nodes = []
    relations = []
    other_relations = []

    # Make sure all items are updated
    diag.canvas.update_now()

    # First extract data from the diagram (which ones are the nodes, and
    # the relationships).
    for item in diag.canvas.get_root_items():
        if isinstance(item, (items.GeneralizationItem,
                             items.ImplementationItem)):
            # Primary relationships, should be drawn top-down
            try:
                relations.append((item.handles[0].connected_to,
                                  item.handles[-1].connected_to))
                primary_nodes.extend(relations[-1])
            except Exception as e:
                log.error(e)
        elif isinstance(item, items.DiagramLine):
            # Secondary (associations, dependencies) may be drawn top-down
            # or left-right
            try:
                other_relations.append((item.handles[0].connected_to,
                                        item.handles[-1].connected_to))
                #other_relations.append((item.handles[-1].connected_to,
                #                        item.handles[0].connected_to))
            except Exception as e:
                log.error(e)
        else:
            nodes.append(item)

    # Add some randomness:
    random.shuffle(other_relations)
    primary_nodes = uniq(primary_nodes)

    # Find out our horizontal and vertical sorting
    sorted = toposort.toposort(nodes, relations, 0)
    other_sorted = toposort.toposort(nodes, other_relations, 0)

    if not sorted:
        return;

    # Move nodes from the first (generalization) row to the other rows
    # if they are not superclasses for some other class
    # Run the list twice, just to ensure no items are left behind.
    for item in list(sorted[0]) * 2:
        if item not in primary_nodes and item in sorted[0]:
            # Find nodes that do have a relation to this one
            related = find_related_nodes(item, other_relations)
            # Figure out what row(s) they're on
            row = find_row(item, related, sorted[1:])
            if row:
                #print 'moving', item.subject.name, 'to row', sorted.index(row)
                sorted[0].remove(item)
                row.append(item)

    # Order each row based on the sort order of other_sorted
    # (the secondary sort alg.).
    for row in sorted:
        for other_row in other_sorted:
            for other_item in other_row:
                if other_item in row:
                    row.remove(other_item)
                    row.append(other_item)

    # Place the nodes on the diagram.
    y = old_div(MARGIN, 2)
    for row in sorted:
        x = old_div(MARGIN, 2)
        maxy = 0
        for item in row:
            if not item:
                continue
            maxy = max(maxy, item.height)
            a = item.matrix
            a = (a[0], a[1], a[2], a[3], x, y)
            item.matrix = a
            item.request_update()
            x += item.width + MARGIN
        y += maxy + MARGIN

    # Reattach the relationships to the nodes, in a way that it looks nice.
    simple_layout_lines(diag)


def simple_layout_lines(diag):
    """
    Just do the layout of the lines in a diagram. The nodes (class, package)
    are left where they are (use layout_diagram() if you want to reorder
    everything).

    The line layout is basically very simple: just draw straight lines
    between nodes on the diagram.
    """
    lines = {}
    for item in diag.canvas.get_root_items():
        if isinstance(item, items.DiagramLine):
            # Secondary (associations, dependencies) may be drawn top-down
            # or left-right
            try:
                lines[item] = (item.handles[0].connected_to,
                               item.handles[-1].connected_to)
            except Exception as e:
                log.error(e)

    # Now we have the lines, let's first ensure we only have a begin and an
    # end handle
    for line in lines.keys():
        while len(line.handles) > 2:
            line.set_property('del_segment', 0)

    # Strategy 1:
    # Now we have nice short lines. Let's move them to a point between
    # both nodes and let the connect() do the work:
    for line, nodes in lines.items():
        if not nodes[0] or not nodes[1]:
            # loose end
            continue
        center0 = find_center(nodes[0])
        center1 = find_center(nodes[1])
        center = old_div((center0[0] + center1[0]), 2.0), old_div((center0[1] + center1[1]), 2.0)
        line.handles[0].set_pos_w(*center)
        line.handles[-1].set_pos_w(*center)
        nodes[0].connect_handle(line.handles[0])
        nodes[1].connect_handle(line.handles[-1])


def uniq(lst):
    d = {}
    for l in lst:
        d[l] = None
    return d.keys()


def find_related_nodes(item, relations):
    """
    Find related nodes of item, given a list of tuples.
    References to itself are ignored.
    """
    related = []
    for pair in relations:
        if pair[0] is item:
            if pair[1] is not item:
                related.append(pair[1])
        elif pair[1] is item:
            if pair[0] is not item:
                related.append(pair[0])
    return uniq(related)


def find_row(item, related_items, sorted):
    """
    Find the row that contains the most references to item.
    """
    max_refs = 0
    max_row = None
    for row in sorted:
        cnt = len([ i for i in row if i in related_items ])
        if cnt > max_refs:
            max_row = row
            max_refs = cnt
    return max_row

def find_center(item):
    """
    Find the center point of the item, in world coordinates
    """
    x = old_div(item.width, 2.0)
    y = old_div(item.height, 2.0)
    return item.canvas.get_matrix_i2c(item).transform_point(x, y)

# vim:sw=4:et
