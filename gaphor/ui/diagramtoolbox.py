"""
This module contains the actions used in the Toolbox (lower left section
of the main window.

The Toolbox is bound to a diagram. When a diagram page (tab) is switched,
the actions bound to the toolbuttons should change as well.
"""

from gaphor import UML
from gaphor.diagram import items
from gaphor.core import _, inject, radio_action, build_action_group
from diagramtools import PlacementTool, DefaultTool


class DiagramToolbox(object):

    TOOLBOX_ACTIONS = (
        ('toolbox-pointer', _('Pointer'), 'gaphor-pointer'),
        ('toolbox-comment', _('Comment'), 'gaphor-comment'),
        ('toolbox-comment-line', _('Comment line'), 'gaphor-comment-line'),
        ('toolbox-class', _('Class'), 'gaphor-class'),
        ('toolbox-implementation', _('Implementation'), 'gaphor-implementation'),
        )


    element_factory = inject('element_factory')
    properties = inject('properties')


    def __init__(self, view=None):
        self.view = view
        self.action_group = build_action_group(self)

    diagram = property(lambda s: s.view.diagram)
    namespace = property(lambda s: s.view.diagram.namespace)

    @radio_action(names=zip(*TOOLBOX_ACTIONS)[0],
                  labels=zip(*TOOLBOX_ACTIONS)[1],
                  stock_ids=zip(*TOOLBOX_ACTIONS)[2])
    def _set_toolbox_action(self, id):
        """
        Activate a tool based on its index in the TOOLBOX_ACTIONS list.
        """
        tool = self.TOOLBOX_ACTIONS[id][0]
        log.info('Selected item %d: %s' % (id, tool))
        getattr(self, tool.replace('-', '_'))()

    def _after_handler(self):
        if self.properties('reset-tool-after-create', False):
            self.action_group.get_action('toolbox-pointer').activate()
            # TODO: if the item is a NamedItem, start the EditTool.

    def toolbox_pointer(self):
        if self.view:
            self.view.tool = DefaultTool()

    def toolbox_comment(self):
        def item_factory():
            subject = self.element_factory.create(UML.Comment)
            return self.diagram.create(items.CommentItem, subject=subject)

        self.view.tool = PlacementTool(item_factory=item_factory,
                                       after_handler=self._after_handler)

    def toolbox_comment_line(self):
        def item_factory():
            return self.diagram.create(items.CommentLineItem)

        self.view.tool = PlacementTool(item_factory=item_factory,
                                       after_handler=self._after_handler)

    def toolbox_class(self):
        def item_factory():
            subject = self.element_factory.create(UML.Class)
            subject.package = self.namespace
            subject.name = 'NewClass'
            return self.diagram.create(items.ClassItem, subject=subject)

        self.view.tool = PlacementTool(item_factory=item_factory,
                                       after_handler=self._after_handler)

    def toolbox_implementation(self):
        def item_factory():
            return self.diagram.create(items.ImplementationItem)

        self.view.tool = PlacementTool(item_factory=item_factory,
                                       after_handler=self._after_handler)

# vim:sw=4:et:ai
