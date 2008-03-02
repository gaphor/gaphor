from gaphor.diagram.nameditem import NamedItem

class VertexItem(NamedItem):
    """
    Abstract class for all vertices. All state, pseudostate items derive
    from VertexItem, which simplifies transition connection adapters.
    """
    pass

