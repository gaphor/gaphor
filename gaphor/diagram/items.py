"""
All Item's defined in the diagram package. This module
is a shorthand for importing each module individually.
"""

# Base classes:
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.diagramline import DiagramLine, NamedLine
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.classifier import ClassifierItem

# General:
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem

# Classes:
from gaphor.diagram.feature import FeatureItem, AttributeItem, OperationItem
from gaphor.diagram.klass import ClassItem
from gaphor.diagram.interface import InterfaceItem
from gaphor.diagram.package import PackageItem
from gaphor.diagram.association import AssociationItem
from gaphor.diagram.dependency import DependencyItem
from gaphor.diagram.generalization import GeneralizationItem
from gaphor.diagram.implementation import ImplementationItem

# Components:
from gaphor.diagram.artifact import ArtifactItem
from gaphor.diagram.component import ComponentItem
from gaphor.diagram.node import NodeItem

# Actions:
from gaphor.diagram.action import ActionItem
from gaphor.diagram.activitynodes import ActivityNodeItem
from gaphor.diagram.activitynodes import InitialNodeItem, ActivityFinalNodeItem
from gaphor.diagram.activitynodes import FlowFinalNodeItem
from gaphor.diagram.activitynodes import DecisionNodeItem
from gaphor.diagram.activitynodes import ForkNodeItem
from gaphor.diagram.flow import FlowItem
from gaphor.diagram.objectnode import ObjectNodeItem

# Use Cases:
from gaphor.diagram.actor import ActorItem
from gaphor.diagram.usecase import UseCaseItem
from gaphor.diagram.include import IncludeItem
from gaphor.diagram.extend import ExtendItem

# Stereotypes:
from gaphor.diagram.extension import ExtensionItem

