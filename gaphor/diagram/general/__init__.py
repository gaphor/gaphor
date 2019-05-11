from .comment import CommentItem
from .commentline import CommentLineItem
from .simpleitem import Box, Ellipse, Line


def _load():
    from . import connectors, generalpropertypages


_load()
