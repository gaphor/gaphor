from gaphas.connector import Handle, Port

from gaphor import UML
from gaphor.diagram.connectors import Connector
from gaphor.UML.actions.action import ActionItem, ValueSpecificationActionItem
from gaphor.UML.actions.pin import InputPinItem, OutputPinItem, PinItem


@Connector.register(ActionItem, PinItem)
class ActionPinConnector:
    def __init__(
        self,
        action: ActionItem,
        pin: PinItem,
    ) -> None:
        assert action.diagram is pin.diagram
        self.action = action
        self.pin = pin

    def allow(self, handle: Handle, port: Port) -> bool:
        return bool(self.action.diagram) and self.action.diagram is self.pin.diagram

    def connect(self, handle: Handle, port: Port) -> bool:
        """Connect and reconnect at model level.

        Returns `True` if a connection is established.
        """
        pin = self.pin
        if not pin.subject:
            pin.subject = pin.model.create(
                UML.InputPin if isinstance(pin, InputPinItem) else UML.OutputPin
            )

        assert isinstance(pin.subject, (UML.InputPin, UML.OutputPin))
        pin.subject.opaqueAction = self.action.subject

        # This raises the item in the item hierarchy
        pin.change_parent(self.action)

        return True

    def disconnect(self, handle: Handle) -> None:
        pin = self.pin
        if pin.subject and pin.diagram:
            del pin.subject
            pin.change_parent(None)


@Connector.register(ValueSpecificationActionItem, PinItem)
class ValueSpecificationActionPinConnector(ActionPinConnector):
    def allow(self, handle: Handle, port: Port) -> bool:
        return (
            super().allow(handle, port)
            and not len(self.action.subject.outputValue)
            and isinstance(self.pin, OutputPinItem)
            and not self.pin.subject
        )
