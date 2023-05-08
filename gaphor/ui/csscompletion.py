from __future__ import annotations

import tinycss2.color3
from gi.repository import Gio, GObject, Gtk, GtkSource

from gaphor.core.styling import Style


class CompletionProviderBase(GObject.GObject, GtkSource.CompletionProvider):
    def __init__(self, priority: int):
        super().__init__()
        self._priority = priority
        self._filter_data: FilterData = FilterData()

    def proposals(self) -> Gio.ListStore:
        raise NotImplementedError()

    def proposal_text(self, proposal: GtkSource.CompletionProposal) -> str:
        raise NotImplementedError()

    def position_cursor(self, buffer, cursor):
        pass

    def do_activate(
        self,
        context: GtkSource.CompletionContext,
        proposal: GtkSource.CompletionProposal,
    ) -> None:
        buffer = context.get_buffer()
        buffer.begin_user_action()
        has_selection, begin, end = context.get_bounds()
        if has_selection:
            buffer.delete(begin, end)
        text = self.proposal_text(proposal)
        buffer.insert(begin, text, len(text))
        self.position_cursor(buffer, begin)
        buffer.end_user_action()

    def do_display(
        self,
        context: GtkSource.CompletionContext,
        proposal: GtkSource.CompletionProposal,
        cell: GtkSource.CompletionCell,
    ) -> None:
        if cell.props.column == GtkSource.CompletionColumn.ICON:
            pass
        elif cell.props.column == GtkSource.CompletionColumn.TYPED_TEXT:
            cell.set_text(proposal.text)

    def do_get_priority(self, context: GtkSource.CompletionContext) -> int:
        return self._priority

    def do_get_title(self) -> str:
        return self.__class__.__name__

    def do_populate_async(self, context, cancellable, callback, user_data=None) -> None:
        self._filter_data.word = context.get_word()
        store = self.proposals()

        def filter_fn(proposal, data):
            return proposal.text.startswith(data.word)

        store_filter = Gtk.CustomFilter.new(filter_fn, self._filter_data)
        proposals = Gtk.FilterListModel.new(store, store_filter)
        context.set_proposals_for_provider(self, proposals)

    def do_refilter(
        self, context: GtkSource.CompletionContext, model: Gio.ListModel
    ) -> None:
        word = context.get_word()
        change = Gtk.FilterChange.DIFFERENT
        if old_word := self._filter_data.word:
            if word.startswith(old_word):
                change = Gtk.FilterChange.MORE_STRICT
            elif old_word.startswith(word):
                change = Gtk.FilterChange.LESS_STRICT
        self._filter_data.word = word
        model.get_filter().changed(change)


class CssNamedColorsCompletionProvider(CompletionProviderBase):
    def __init__(self):
        super().__init__(priority=-4)

    def proposal_text(self, proposal: GtkSource.CompletionProposal) -> str:
        return proposal.text  # type: ignore[no-any-return]

    def proposals(self):
        store = Gio.ListStore.new(CssNamedColorProposal)
        for color_name in tinycss2.color3._COLOR_KEYWORDS:
            proposal = CssNamedColorProposal(color_name)
            store.append(proposal)
        return store


class CssNamedColorProposal(GObject.Object, GtkSource.CompletionProposal):
    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class CssFunctionCompletionProvider(CompletionProviderBase):
    FUNCTIONS = [
        "hsl",
        "hsla",
        "rgb",
        "rgba",
    ]

    def __init__(self):
        super().__init__(priority=3)

    def proposal_text(self, proposal: GtkSource.CompletionProposal) -> str:
        return f"{proposal.text}()"

    def position_cursor(self, buffer, cursor):
        cursor.backward_char()
        buffer.place_cursor(cursor)

    def proposals(self):
        store = Gio.ListStore.new(CssFunctionProposal)
        for function in self.FUNCTIONS:
            proposal = CssFunctionProposal(function)
            store.append(proposal)
        return store


class CssFunctionProposal(GObject.Object, GtkSource.CompletionProposal):
    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class CssPropertyCompletionProvider(CompletionProviderBase):
    PROPERTIES = sorted(Style.__optional_keys__)

    def __init__(self):
        super().__init__(priority=1)

    def proposal_text(self, proposal):
        return f"{proposal.text}: "

    def proposals(self):
        store = Gio.ListStore.new(CssPropertyProposal)

        for prop in self.PROPERTIES:
            proposal = CssPropertyProposal(prop)
            store.append(proposal)
        return store


class CssPropertyProposal(GObject.Object, GtkSource.CompletionProposal):
    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class FilterData:
    word: str
