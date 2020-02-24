"""
Connect comments.
"""

import logging

from gaphor import UML
from gaphor.diagram.connectors import BaseConnector, Connector
from gaphor.diagram.general.comment import CommentItem
from gaphor.diagram.general.commentline import CommentLineItem
from gaphor.diagram.presentation import ElementPresentation, LinePresentation

logger = logging.getLogger(__name__)


@Connector.register(CommentItem, CommentLineItem)
@Connector.register(ElementPresentation, CommentLineItem)
class CommentLineElementConnect(BaseConnector):
    """Connect a comment line to any element item."""

    line: CommentLineItem

    def allow(self, handle, port):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        connected_to = self.get_connected(opposite)
        element = self.element

        if connected_to is element:
            return None

        # Same goes for subjects:
        if (
            connected_to
            and (not (connected_to.subject or element.subject))
            and connected_to.subject is element.subject
        ):
            return None

        # One end should be connected to a CommentItem:
        cls = CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        # Do not allow links between the comment and the element
        if (
            connected_to
            and element
            and (
                (
                    isinstance(connected_to.subject, UML.Comment)
                    and self.element.subject in connected_to.subject.annotatedElement
                )
                or (
                    isinstance(self.element.subject, UML.Comment)
                    and connected_to.subject in self.element.subject.annotatedElement
                )
            )
        ):
            return None

        return super().allow(handle, port)

    def connect(self, handle, port):
        if super().connect(handle, port):
            opposite = self.line.opposite(handle)
            connected_to = self.get_connected(opposite)
            if connected_to:
                if isinstance(connected_to.subject, UML.Comment):
                    connected_to.subject.annotatedElement = self.element.subject
                else:
                    assert isinstance(self.element.subject, UML.Comment)
                    self.element.subject.annotatedElement = connected_to.subject

    def disconnect(self, handle):
        opposite = self.line.opposite(handle)
        oct = self.get_connected(opposite)
        hct = self.get_connected(handle)

        if hct and oct:
            logger.debug(f"Disconnecting {hct} and {oct}")
            try:
                if hct.subject and isinstance(oct.subject, UML.Comment):
                    del oct.subject.annotatedElement[hct.subject]
                elif hct.subject and oct.subject:
                    del hct.subject.annotatedElement[oct.subject]
            except ValueError:
                logger.debug(
                    "Invoked CommentLineElementConnect.disconnect() for nonexistent relationship"
                )

        super().disconnect(handle)


@Connector.register(LinePresentation, CommentLineItem)
class CommentLineLineConnect(BaseConnector):
    """Connect a comment line to any diagram line."""

    def allow(self, handle, port):
        """
        In addition to the normal check, both line ends may not be connected
        to the same element. Same goes for subjects.
        One of the ends should be connected to a UML.Comment element.
        """
        opposite = self.line.opposite(handle)
        element = self.element
        connected_to = self.get_connected(opposite)

        # do not connect to the same item nor connect to other comment line
        if (
            connected_to is element
            or not element.subject
            or isinstance(element, CommentLineItem)
        ):
            return None

        # Same goes for subjects:
        if (
            connected_to
            and (not (connected_to.subject or element.subject))
            and connected_to.subject is element.subject
        ):
            return None

        # One end should be connected to a CommentItem:
        cls = CommentItem
        glue_ok = isinstance(connected_to, cls) ^ isinstance(self.element, cls)
        if connected_to and not glue_ok:
            return None

        return super().allow(handle, port)

    def connect(self, handle, port):
        if super().connect(handle, port):
            opposite = self.line.opposite(handle)
            c = self.get_connected(opposite)
            if c and self.element.subject:
                if isinstance(c.subject, UML.Comment):
                    c.subject.annotatedElement = self.element.subject
                else:
                    assert isinstance(self.element.subject, UML.Comment)
                    self.element.subject.annotatedElement = c.subject

    def disconnect(self, handle):
        c1 = self.get_connected(handle)
        opposite = self.line.opposite(handle)
        c2 = self.get_connected(opposite)
        if c1 and c2:
            if (
                isinstance(c1.subject, UML.Comment)
                and c2.subject in c1.subject.annotatedElement
            ):
                del c1.subject.annotatedElement[c2.subject]
            elif c2.subject and c1.subject in c2.subject.annotatedElement:
                del c2.subject.annotatedElement[c1.subject]
        super().disconnect(handle)


@Connector.register(CommentLineItem, LinePresentation)
class InverseCommentLineLineConnect(CommentLineLineConnect):
    """
    In case a line is disconnected that contains a comment-line,
    the comment line unlinking should happen in a correct way.
    """

    def __init__(self, line, element):
        super().__init__(element, line)
