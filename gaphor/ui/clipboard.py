"""Copy / Paste functionality."""

from __future__ import annotations

import asyncio
import contextlib
import io
from collections.abc import Collection

import cairo
from gi.repository import Gdk, GLib, GObject

from gaphor.core import Transaction
from gaphor.core.modeling import Presentation
from gaphor.diagram.copypaste import copy_full, paste_full, paste_link
from gaphor.diagram.export import render


class CopyBuffer(GObject.Object):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer

    buffer = GObject.Property(type=object)


class Clipboard:
    """Copy/Cut/Paste functionality for diagrams."""

    def __init__(self, event_manager, element_factory, clipboard=None):
        super().__init__()
        self.event_manager = event_manager
        self.element_factory = element_factory

        self.clipboard = clipboard or Gdk.Display.get_default().get_clipboard()
        self._background_task: asyncio.Task | None = None

    def copy(self, view):
        if items := view.selection.selected_items:
            self._copy(view.model, items)

    def cut(self, view):
        items = view.selection.selected_items
        if not items:
            return

        self._copy(view.model, items)

        with Transaction(self.event_manager):
            for i in list(items):
                i.unlink()

    def can_paste(self):
        return (
            self.clipboard.is_local()
            and (content_provider := self.clipboard.get_content())
            and content_provider.ref_formats().contain_gtype(CopyBuffer.__gtype__)
        )

    def paste_link(self, view):
        self.create_background_task(self._paste(view, paste_link))

    def paste_full(self, view):
        self.create_background_task(self._paste(view, paste_full))

    def _copy(self, diagram, items: Collection[Presentation]) -> None:
        if items:
            copy_buffer = copy_full(items, self.element_factory.lookup)
            svg_data = GLib.Bytes.new(render_svg(diagram, items))
            png_data = GLib.Bytes.new(render_png(diagram, items))

            self.clipboard.set_content(
                Gdk.ContentProvider.new_union(
                    [
                        Gdk.ContentProvider.new_for_value(
                            GObject.Value(
                                CopyBuffer.__gtype__, CopyBuffer(buffer=copy_buffer)
                            )
                        ),
                        Gdk.ContentProvider.new_for_bytes("image/svg", svg_data),
                        Gdk.ContentProvider.new_for_bytes("image/png", png_data),
                    ]
                )
            )

    async def _paste(self, view, paster):
        diagram = view.model

        try:
            copy_buffer = await self.clipboard.read_value_async(
                CopyBuffer.__gtype__, io_priority=GLib.PRIORITY_DEFAULT
            )
        except GLib.GError as e:
            if str(e).startswith("g-io-error-quark:"):
                return
            raise

        with Transaction(self.event_manager):
            # Create new id's that have to be used to create the items:
            new_items = paster(copy_buffer.buffer, diagram)

            # move pasted items a bit, so user can see result of his action :)
            for item in new_items:
                if item.parent not in new_items:
                    item.matrix.translate(10, 10)

        selection = view.selection
        selection.unselect_all()
        selection.select_items(*new_items)

    def create_background_task(self, coro) -> asyncio.Task:
        assert self._background_task is None or self._background_task.done()
        task = asyncio.create_task(coro)
        self._background_task = task

        def task_done(task):
            assert self._background_task is task
            self._background_task = None

        task.add_done_callback(task_done)
        return task

    def cancel_background_task(self) -> bool:
        return (self._background_task is not None) and self._background_task.cancel()

    async def gather_background_task(self):
        if self._background_task:
            await asyncio.gather(self._background_task)


def render_svg(diagram, items) -> bytes:
    buffer = io.BytesIO()
    render(
        diagram,
        lambda w, h: cairo.SVGSurface(buffer, w, h),
        items=items,
        with_diagram_type=False,
    )
    return buffer.getbuffer()


def render_png(diagram, items) -> bytes:
    @contextlib.contextmanager
    def new_png_surface(w, h):
        with cairo.ImageSurface(cairo.FORMAT_ARGB32, int(w + 1), int(h + 1)) as surface:
            yield surface
            surface.write_to_png(buffer)

    buffer = io.BytesIO()
    render(diagram, new_png_surface, items=items, with_diagram_type=False)
    return buffer.getbuffer()
