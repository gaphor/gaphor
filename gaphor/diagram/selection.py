from typing import Optional

from gaphas.item import Item
from gaphas.view.selection import Selection as _Selection


class Selection(_Selection):
    def __init__(self):
        super().__init__()
        self._dropzone_item: Optional[Item] = None

    def clear(self):
        self._dropzone_item = None
        super().clear()

    @property
    def dropzone_item(self) -> Optional[Item]:
        return self._dropzone_item

    @dropzone_item.setter
    def dropzone_item(self, item: Optional[Item]) -> None:
        if item is not self._dropzone_item:
            self._dropzone_item = item
