"""
A collection of some (abstract) base types, or marker interfaces,
that can be used to identify groups of similar items.
"""


class Named:
    """
    Marker for any named presentations.
    """

    pass


class Classified(Named):
    """
    Marker for Classified presentations.
    """

    pass
