from gaphor.core import transactional
from gaphor.diagram.propertypages import (
    ComboModel,
    PropertyPageBase,
    PropertyPages,
    new_resource_builder,
)
from gaphor.UML.interactions.interactionsconnect import get_lifeline
from gaphor.UML.interactions.message import MessageItem

new_builder = new_resource_builder("gaphor.UML.interactions")


@PropertyPages.register(MessageItem)
class MessagePropertyPage(PropertyPageBase):
    """Property page for editing message items.

    When message is on communication diagram, then additional messages
    can be added. On sequence diagram sort of message can be changed.
    """

    order = 15

    MESSAGE_SORT = [
        ("Call", "synchCall"),
        ("Asynchronous", "asynchCall"),
        ("Signal", "asynchSignal"),
        ("Create", "createMessage"),
        ("Delete", "deleteMessage"),
        ("Reply", "reply"),
    ]

    def __init__(self, item):
        self.item = item

    def construct(self):
        item = self.item
        subject = item.subject

        if not subject or item.is_communication():
            return

        builder = new_builder(
            "message-editor",
            signals={"message-combo-changed": (self._on_message_sort_change,)},
        )

        sort_data = self.MESSAGE_SORT
        lifeline = get_lifeline(item, item.tail)

        # disallow connecting two delete messages to a lifeline
        if (
            lifeline
            and lifeline.is_destroyed
            and subject.messageSort != "deleteMessage"
        ):
            sort_data = sort_data.copy()
            assert sort_data[4][1] == "deleteMessage"
            del sort_data[4]

        self.model = ComboModel(sort_data)
        combo = builder.get_object("message-combo")
        combo.set_model(self.model)

        index = self.model.get_index(subject.messageSort)
        combo.set_active(index)

        return builder.get_object("message-editor")

    @transactional
    def _on_message_sort_change(self, combo):
        """Update message item's message sort information."""
        ms = self.model.get_value(combo.get_active())

        item = self.item
        subject = item.subject
        lifeline = get_lifeline(item, item.tail)

        # allow only one delete message to connect to lifeline's lifetime
        # destroyed status can be changed only by delete message itself
        if lifeline and (
            subject.messageSort == "deleteMessage" or not lifeline.is_destroyed
        ):
            is_destroyed = ms == "deleteMessage"
            lifeline.is_destroyed = is_destroyed
            lifeline.request_update()

        subject.messageSort = ms
        item.request_update()
