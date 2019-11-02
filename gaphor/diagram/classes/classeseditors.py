from typing import Optional

from gaphor import UML
from gaphor.diagram.editors import Editor, AbstractEditor
from gaphor.diagram.classes.association import AssociationItem


@Editor.register(AssociationItem)
class AssociationItemEditor(AbstractEditor):
    def __init__(self, item):
        self._item = item
        self._edit: Optional[AssociationItem] = None

    def is_editable(self, x, y):
        """Find out what's located at point (x, y), is it in the
        name part or is it text in some compartment
        """
        item = self._item
        if not item.subject:
            return False
        if item.head_end.point((x, y)) <= 0:
            self._edit = item.head_end
        elif item.tail_end.point((x, y)) <= 0:
            self._edit = item.tail_end
        else:
            self._edit = item
        return True

    def get_text(self):
        assert self._edit
        if self._edit is self._item:
            return self._edit.subject.name
        return UML.format(
            self._edit.subject,
            visibility=True,
            is_derived=True,
            type=True,
            multiplicity=True,
            default=True,
        )

    def update_text(self, text):
        assert self._edit
        UML.parse(self._edit.subject, text)

    def key_pressed(self, pos, key):
        pass
