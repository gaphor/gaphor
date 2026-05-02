import importlib.resources

from gi.repository import Gio, GObject, Pango

from gaphor.core.format import format
from gaphor.core.modeling import Base
from gaphor.diagram.group import Root, RootType
from gaphor.diagram.iconname import icon_name


class TreeItem(GObject.Object):
    def __init__(self, element: Base | None):
        super().__init__()
        self.element = element
        self.sync()

    icon = GObject.Property(type=str)
    icon_visible = GObject.Property(type=bool, default=False)
    readonly_text = GObject.Property(type=str)
    attributes = GObject.Property(type=Pango.AttrList)
    editing = GObject.Property(type=bool, default=False)
    can_edit = GObject.Property(type=bool, default=True)

    @GObject.Property(type=str)
    def editable_text(self):
        element = self.element
        if not element:
            return ""
        return (
            getattr(element, "declaredName", None)
            or getattr(element, "elementId", None)
            or ""
        )

    @editable_text.setter  # type: ignore[no-redef]
    def editable_text(self, text):
        if element := self.element:
            if hasattr(element, "declaredName"):
                element.declaredName = text or ""

    def sync(self) -> None:
        if element := self.element:
            self.readonly_text = format(element)
            self.notify("editable-text")
            self.icon = icon_name(element)
            self.icon_visible = bool(self.icon)
            self.attributes = Pango.AttrList()

    def start_editing(self):
        self.editing = True


class Branch:
    def __init__(self):
        self.elements = Gio.ListStore.new(TreeItem.__gtype__)


class TreeModel:
    def __init__(self, event_manager, element_factory, on_select=None, on_sync=None):
        super().__init__()
        self.branches: dict[TreeItem | RootType, Branch] = {Root: Branch()}
        self._on_select = on_select
        self._on_sync = on_sync
        self.event_manager = event_manager
        self.element_factory = element_factory

    def shutdown(self) -> None:
        pass

    @property
    def root(self) -> Gio.ListStore:
        return self.branches[Root].elements

    @property
    def template(self) -> str:
        return (importlib.resources.files("gaphor.SysML2") / "treeitem.ui").read_text(
            encoding="utf-8"
        )

    def child_model(self, item: TreeItem) -> Gio.ListStore | None:
        return None

    def tree_item_sort(self, a, b) -> int:
        return 0

    def should_expand(self, item: TreeItem, element: Base) -> bool:
        return False
