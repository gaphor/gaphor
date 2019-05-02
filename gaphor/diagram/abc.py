import abc


class ConnectBase(metaclass=abc.ABCMeta):
    """
    This interface is used by the HandleTool to allow connecting
    lines to element items. For each specific case (Element, Line) an
    adapter could be written.
    """

    @abc.abstractmethod
    def connect(self, handle, port):
        """
        Connect a line's handle to element.

        Note that at the moment of the connect, handle.connected_to may point
        to some other item. The implementor should do the disconnect of
        the other element themselves.
        """

    @abc.abstractmethod
    def disconnect(self, handle):
        """
        The true disconnect. Disconnect a handle.connected_to from an
        element. This requires that the relationship is also removed at
        model level.
        """
