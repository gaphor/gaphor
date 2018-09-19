#!/usr/bin/env python

# Copyright (C) 2007-2017 Arjan Molenaar <gaphor@gmail.com>
#                         Artur Wroblewski <wrobell@pld-linux.org>
#                         Dan Yeaw <dan@yeaw.me>
#
# This file is part of Gaphor.
#
# Gaphor is free software: you can redistribute it and/or modify it under the
# terms of the GNU Library General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# Gaphor is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Library General Public License 
# more details.
#
# You should have received a copy of the GNU Library General Public 
# along with Gaphor.  If not, see <http://www.gnu.org/licenses/>.
"""
All Item's defined in the diagram package. This module
is a shorthand for importing each module individually.
"""

# Base classes:
from __future__ import absolute_import
from gaphor.diagram.diagramitem import DiagramItem
from gaphor.diagram.diagramline import DiagramLine, NamedLine
from gaphor.diagram.elementitem import ElementItem
from gaphor.diagram.nameditem import NamedItem
from gaphor.diagram.compartment import CompartmentItem, FeatureItem
from gaphor.diagram.classifier import ClassifierItem

# General:
from gaphor.diagram.comment import CommentItem
from gaphor.diagram.commentline import CommentLineItem
from gaphor.diagram.simpleitem import Line, Box, Ellipse

# Classes:
from gaphor.diagram.classes.klass import ClassItem, OperationItem
from gaphor.diagram.classes.interface import InterfaceItem
from gaphor.diagram.classes.package import PackageItem
from gaphor.diagram.classes.association import AssociationItem
from gaphor.diagram.classes.dependency import DependencyItem
from gaphor.diagram.classes.generalization import GeneralizationItem
from gaphor.diagram.classes.implementation import ImplementationItem

# Components:
from gaphor.diagram.artifact import ArtifactItem
from gaphor.diagram.connector import ConnectorItem
from gaphor.diagram.component import ComponentItem
from gaphor.diagram.node import NodeItem
from gaphor.diagram.components.subsystem import SubsystemItem

# Actions:
from gaphor.diagram.activitynodes import ActivityNodeItem
from gaphor.diagram.activitynodes import InitialNodeItem, ActivityFinalNodeItem
from gaphor.diagram.activitynodes import FlowFinalNodeItem
from gaphor.diagram.activitynodes import DecisionNodeItem
from gaphor.diagram.activitynodes import ForkNodeItem
from gaphor.diagram.objectnode import ObjectNodeItem
from gaphor.diagram.actions.action import ActionItem, SendSignalActionItem, AcceptEventActionItem
from gaphor.diagram.actions.flow import FlowItem
from gaphor.diagram.actions.partition import PartitionItem

# Interactions
from gaphor.diagram.interaction import InteractionItem
from gaphor.diagram.lifeline import LifelineItem
from gaphor.diagram.message import MessageItem

# States
from gaphor.diagram.states import VertexItem
from gaphor.diagram.states.state import StateItem
from gaphor.diagram.states.transition import TransitionItem
from gaphor.diagram.states.finalstate import FinalStateItem
from gaphor.diagram.states.pseudostates import InitialPseudostateItem, HistoryPseudostateItem

# Use Cases:
from gaphor.diagram.actor import ActorItem
from gaphor.diagram.usecase import UseCaseItem
from gaphor.diagram.include import IncludeItem
from gaphor.diagram.extend import ExtendItem

# Stereotypes:
from gaphor.diagram.extension import ExtensionItem
from gaphor.diagram.profiles.metaclass import MetaclassItem

