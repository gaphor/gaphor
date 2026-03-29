from gi.repository import GObject

from gaphor.diagram.general.metadata import MetadataItem
from gaphor.diagram.general.simpleitem import Box, Diamond, Ellipse, Line, LineEndStyle
from gaphor.diagram.iconname import to_kebab_case
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_builder,
)
from gaphor.transaction import Transaction


class LabelPropertyBinding(GObject.Object):
    def __init__(self, item, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager
        self.watcher = item.watcher()
        self.watcher.watch("label", lambda *_: self.notify("label"))

    def do_dispose(self):
        self.watcher.unsubscribe_all()

    @GObject.Property(type=str)
    def label(self) -> str:
        return self.item.label or ""

    @label.setter  # type: ignore[no-redef]
    def label(self, label: str):
        with Transaction(self.event_manager, context="editing"):
            self.item.label = label


@PropertyPages.register(Box)
@PropertyPages.register(Diamond)
@PropertyPages.register(Ellipse)
@PropertyPages.register(Line)
class LabelPropertyPage(PropertyPageBase):
    order = 10

    def __init__(self, item, event_manager):
        super().__init__()
        self.binding = LabelPropertyBinding(item, event_manager) if item else None

    def construct(self):
        if not self.binding:
            return

        builder = new_builder(
            "label-editor",
            binding=self.binding,
        )

        return builder.get_object("label-editor")

    def close(self):
        if self.binding:
            self.binding.run_dispose()


class LineEndPropertyBinding(GObject.Object):
    LINE_END_STYLES: tuple[LineEndStyle, ...] = (
        LineEndStyle.none,
        LineEndStyle.arrow,
        LineEndStyle.triangle,
        LineEndStyle.diamond,
    )

    def __init__(self, item, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager
        self.watcher = item.watcher()
        self.watcher.watch("head_end", lambda *_: self.notify("head_end"))
        self.watcher.watch("tail_end", lambda *_: self.notify("tail_end"))

    def do_dispose(self):
        self.watcher.unsubscribe_all()

    @GObject.Property(type=int)
    def head_end(self) -> int:
        return self.LINE_END_STYLES.index(self.item.head_end)

    @head_end.setter  # type: ignore[no-redef]
    def head_end(self, selected: int):
        if 0 <= selected < len(self.LINE_END_STYLES):
            with Transaction(self.event_manager, context="editing"):
                self.item.head_end = self.LINE_END_STYLES[selected]

    @GObject.Property(type=int)
    def tail_end(self) -> int:
        return self.LINE_END_STYLES.index(self.item.tail_end)

    @tail_end.setter  # type: ignore[no-redef]
    def tail_end(self, selected: int):
        if 0 <= selected < len(self.LINE_END_STYLES):
            with Transaction(self.event_manager, context="editing"):
                self.item.tail_end = self.LINE_END_STYLES[selected]


@PropertyPages.register(Line)
class LineEndPropertyPage(PropertyPageBase):
    order = 11

    def __init__(self, item, event_manager):
        super().__init__()
        self.binding = LineEndPropertyBinding(item, event_manager) if item else None

    def construct(self):
        if not self.binding:
            return

        builder = new_builder(
            "line-end-editor",
            binding=self.binding,
        )

        return builder.get_object("line-end-editor")

    def close(self):
        if self.binding:
            self.binding.run_dispose()


@PropertyPages.register(MetadataItem)
class MetadataPropertyPage(PropertyPageBase):
    def __init__(self, item, event_manager):
        self.item = item
        self.event_manager = event_manager
        self.watcher = item and item.watcher()

    def construct(self):
        attrs = [
            "createdBy",
            "description",
            "website",
            "revision",
            "license",
            "createdOn",
            "updatedOn",
        ]

        builder = new_builder(
            "metadata-editor",
            signals={
                f"{to_kebab_case(a)}-changed": (self._on_field_change, a) for a in attrs
            },
        )

        item = self.item

        for a in attrs:
            builder.get_object(f"{to_kebab_case(a)}").set_text(getattr(item, a) or "")

        return builder.get_object("metadata-editor")

    def _on_field_change(self, entry, field_name):
        with Transaction(self.event_manager, context="editing"):
            text = entry.get_text()
            setattr(self.item, field_name, text)
