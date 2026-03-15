from gi.repository import GObject

from gaphor.diagram.general.metadata import MetadataItem
from gaphor.diagram.general.simpleitem import Box, Ellipse, Line
from gaphor.diagram.iconname import to_kebab_case
from gaphor.diagram.propertypages import (
    PropertyPageBase,
    PropertyPages,
    new_builder,
)
from gaphor.transaction import Transaction


class DisposeWarning(RuntimeWarning):
    pass


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
@PropertyPages.register(Ellipse)
@PropertyPages.register(Line)
class LabelPropertyPage(PropertyPageBase):
    order = 10

    def __init__(self, item, event_manager):
        super().__init__()
        self.item = item
        self.event_manager = event_manager

    def construct(self):
        if not self.item:
            return

        builder = new_builder(
            "label-editor",
            binding=LabelPropertyBinding(self.item, self.event_manager),
        )

        return builder.get_object("label-editor")


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
