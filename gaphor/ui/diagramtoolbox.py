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

__all__ = [ 'DiagramToolbox', 'TOOLBOX_ACTIONS' ]

TOOLBOX_ACTIONS = (
    ('', (
        ('toolbox-pointer', _('Pointer'), 'gaphor-pointer'),
        ('toolbox-comment', _('Comment'), 'gaphor-comment'),
        ('toolbox-comment-line', _('Comment line'), 'gaphor-comment-line'),
    )), (_('Classes'), (
        ('toolbox-class', _('Class'), 'gaphor-class'),
        ('toolbox-interface', _('Interface'), 'gaphor-interface'),
        ('toolbox-package', _('Package'), 'gaphor-package'),
        ('toolbox-association', _('Association'), 'gaphor-association'),
        ('toolbox-dependency', _('Dependency'), 'gaphor-dependency'),
        ('toolbox-generalization', _('Generalization'), 'gaphor-generalization'),
        ('toolbox-implementation', _('Implementation'), 'gaphor-implementation'),
    )), (_('Components'), (
        ('toolbox-component', _('Component'), 'gaphor-component'),
#        ('toolbox-assembly-connector', _('Assembly connector'), 'gaphor-assembly-connector'),
        ('toolbox-node', _('Node'), 'gaphor-node'),
        ('toolbox-artifact', _('Artifact'), 'gaphor-artifact'),
    )),
    )
##        (_('Composite Structures'), (
##                'InsertConnector',)),
#        (_('Actions'), (
#                'InsertAction',
#                'InsertInitialNode',
#                'InsertActivityFinalNode',
#                'InsertFlowFinalNode',
#                'InsertDecisionNode',
#                'InsertForkNode',
#                'InsertObjectNode',
#                'InsertFlow')),
##        (_('Interactions'), (
##                'InsertInteraction',
##                'InsertLifeline',
##                'InsertMessage')),
#        (_('Use Cases'), (
#                'InsertUseCase',
#                'InsertActor',
#                'InsertUseCaseAssociation',
#                'InsertInclude',
#                'InsertExtend')),
#        (_('Profiles'), (
#                'InsertProfile',
#                'InsertMetaClass',
#                'InsertStereotype',
#                'InsertExtension')),


def itemiter(toolbox_actions):
    """
    Iterate toolbox items, irregardless section headers
    """
    for name, section in toolbox_actions:
        for e in section:
            yield e


class DiagramToolbox(object):
    """
    Composite class for DiagramTab (diagramtab.py).
    """

    element_factory = inject('element_factory')
    properties = inject('properties')


    def __init__(self, view=None):
        self.view = view
        self.action_group = build_action_group(self)

    diagram = property(lambda s: s.view.diagram)
    namespace = property(lambda s: s.view.diagram.namespace)

    @radio_action(names=zip(*list(itemiter(TOOLBOX_ACTIONS)))[0],
                  labels=zip(*list(itemiter(TOOLBOX_ACTIONS)))[1],
                  stock_ids=zip(*list(itemiter(TOOLBOX_ACTIONS)))[2])
    def _set_toolbox_action(self, id):
        """
        Activate a tool based on its index in the TOOLBOX_ACTIONS list.
        """
        tool = list(itemiter(TOOLBOX_ACTIONS))[id][0]
        log.info('Selected item %d: %s' % (id, tool))
        getattr(self, tool.replace('-', '_'))()

    def _item_factory(self, item_class, subject_class=None):
        def factory_method():
            if subject_class:
                subject = self.element_factory.create(subject_class)
                return self.diagram.create(item_class, subject=subject)
            return self.diagram.create(item_class)
        return factory_method

    def _namespace_item_factory(self, item_class, subject_class):
        """
        Returns a factory method for Namespace classes.
        To be used by the PlacementTool.
        """
        def factory_method():
            subject = self.element_factory.create(subject_class)
            subject.package = self.namespace
            subject.name = 'New%s' % subject_class.__name__
            return self.diagram.create(item_class, subject=subject)
        return factory_method

    def _after_handler(self):
        if self.properties('reset-tool-after-create', False):
            self.action_group.get_action('toolbox-pointer').activate()
            # TODO: if the item is a NamedItem, start the EditTool.


    ##
    ## Toolbox actions
    ##

    def toolbox_pointer(self):
        if self.view:
            self.view.tool = DefaultTool()

    def toolbox_comment(self):
        self.view.tool = PlacementTool(
                item_factory=self._item_factory(items.CommentItem, UML.Comment),
                after_handler=self._after_handler)

    def toolbox_comment_line(self):
        self.view.tool = PlacementTool(
                item_factory=self._item_factory(items.CommentLineItem),
                after_handler=self._after_handler)

    # Classes:

    def toolbox_class(self):
        self.view.tool = PlacementTool(
                item_factory=self._namespace_item_factory(items.ClassItem,
                                                          UML.Class),
                after_handler=self._after_handler)

    def toolbox_interface(self):
        self.view.tool = PlacementTool(
                item_factory=self._namespace_item_factory(items.InterfaceItem,
                                                          UML.Interface),
                after_handler=self._after_handler)

    def toolbox_package(self):
        self.view.tool = PlacementTool(
                item_factory=self._namespace_item_factory(items.PackageItem,
                                                          UML.Package),
                after_handler=self._after_handler)

    def toolbox_association(self):
        self.view.tool = PlacementTool(
                item_factory=self._item_factory(items.AssociationItem),
                after_handler=self._after_handler)

    def toolbox_dependency(self):
        self.view.tool = PlacementTool(
                item_factory=self._item_factory(items.DependencyItem),
                after_handler=self._after_handler)

    def toolbox_generalization(self):
        self.view.tool = PlacementTool(
                item_factory=self._item_factory(items.GeneralizationItem),
                after_handler=self._after_handler)

    def toolbox_implementation(self):
        self.view.tool = PlacementTool(
                item_factory=self._item_factory(items.ImplementationItem),
                after_handler=self._after_handler)

    # Components:

    def toolbox_component(self):
        self.view.tool = PlacementTool(
                item_factory=self._namespace_item_factory(items.ComponentItem,
                                                          UML.Component),
                after_handler=self._after_handler)

    def toolbox_node(self):
        self.view.tool = PlacementTool(
                item_factory=self._namespace_item_factory(items.NodeItem,
                                                          UML.Node),
                after_handler=self._after_handler)

    def toolbox_artifact(self):
        self.view.tool = PlacementTool(
                item_factory=self._namespace_item_factory(items.ArtifactItem,
                                                          UML.Artifact),
                after_handler=self._after_handler)

    # Actions:

    # Interactions:

    # Use cases:

    # Profiles:


# vim:sw=4:et:ai
