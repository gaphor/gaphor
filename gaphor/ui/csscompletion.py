from __future__ import annotations

from gi.repository import Gio, GObject, Gtk, GtkSource

from gaphor.core.styling import Style


class CssNamedColorsCompletionProvider(GObject.GObject, GtkSource.CompletionProvider):
    # https://www.w3.org/TR/css-color-4/
    COLORS = [
        "aliceblue",
        "antiquewhite",
        "aqua",
        "aquamarine",
        "azure",
        "beige",
        "bisque",
        "black",
        "blanchedalmond",
        "blue",
        "blueviolet",
        "brown",
        "burlywood",
        "cadetblue",
        "chartreuse",
        "chocolate",
        "coral",
        "cornflowerblue",
        "cornsilk",
        "crimson",
        "cyan",
        "darkblue",
        "darkcyan",
        "darkgoldenrod",
        "darkgray",
        "darkgreen",
        "darkgrey",
        "darkkhaki",
        "darkmagenta",
        "darkolivegreen",
        "darkorange",
        "darkorchid",
        "darkred",
        "darksalmon",
        "darkseagreen",
        "darkslateblue",
        "darkslategray",
        "darkslategrey",
        "darkturquoise",
        "darkviolet",
        "deeppink",
        "deepskyblue",
        "dimgray",
        "dimgrey",
        "dodgerblue",
        "firebrick",
        "floralwhite",
        "forestgreen",
        "fuchsia",
        "gainsboro",
        "ghostwhite",
        "gold",
        "goldenrod",
        "gray",
        "green",
        "greenyellow",
        "grey",
        "honeydew",
        "hotpink",
        "indianred",
        "indigo",
        "ivory",
        "khaki",
        "lavender",
        "lavenderblush",
        "lawngreen",
        "lemonchiffon",
        "lightblue",
        "lightcoral",
        "lightcyan",
        "lightgoldenrodyellow",
        "lightgray",
        "lightgreen",
        "lightgrey",
        "lightpink",
        "lightsalmon",
        "lightseagreen",
        "lightskyblue",
        "lightslategray",
        "lightslategrey",
        "lightsteelblue",
        "lightyellow",
        "lime",
        "limegreen",
        "linen",
        "magenta",
        "maroon",
        "mediumaquamarine",
        "mediumblue",
        "mediumorchid",
        "mediumpurple",
        "mediumseagreen",
        "mediumslateblue",
        "mediumspringgreen",
        "mediumturquoise",
        "mediumvioletred",
        "midnightblue",
        "mintcream",
        "mistyrose",
        "moccasin",
        "navajowhite",
        "navy",
        "oldlace",
        "olive",
        "olivedrab",
        "orange",
        "orangered",
        "orchid",
        "palegoldenrod",
        "palegreen",
        "paleturquoise",
        "palevioletred",
        "papayawhip",
        "peachpuff",
        "peru",
        "pink",
        "plum",
        "powderblue",
        "purple",
        "rebeccapurple",
        "red",
        "rosybrown",
        "royalblue",
        "saddlebrown",
        "salmon",
        "sandybrown",
        "seagreen",
        "seashell",
        "sienna",
        "silver",
        "skyblue",
        "slateblue",
        "slategray",
        "slategrey",
        "snow",
        "springgreen",
        "steelblue",
        "tan",
        "teal",
        "thistle",
        "tomato",
        "turquoise",
        "violet",
        "wheat",
        "white",
        "whitesmoke",
        "yellow",
        "yellowgreen",
    ]

    def __init__(self):
        super().__init__()
        self._filter_data: FilterData = FilterData()

    def do_activate(self, context: GtkSource.CompletionContext, proposal: GtkSource.CompletionProposal) -> None:
        buffer = context.get_buffer()
        buffer.begin_user_action()
        has_selection, begin, end = context.get_bounds()
        if has_selection:
            buffer.delete(begin, end)
        buffer.insert(begin, proposal.text, len(proposal.text))
        buffer.end_user_action()

    def do_display(self, context: GtkSource.CompletionContext, proposal: GtkSource.CompletionProposal, cell: GtkSource.CompletionCell) -> None:
        if cell.props.column == GtkSource.CompletionColumn.ICON:
            pass
        elif cell.props.column == GtkSource.CompletionColumn.TYPED_TEXT:
            cell.set_text(proposal.text)

    def do_get_priority(self, context: GtkSource.CompletionContext) -> int:
        return -4

    def do_get_title(self) -> str:
        return "Colors"

    def do_populate_async(self, context, cancellable, callback, user_data=None) -> None:
        task = Gio.Task.new(self, cancellable, callback)
        store = Gio.ListStore.new(CssNamedColorProposal)
        self._filter_data.word = context.get_word()

        for color in self.COLORS:
            proposal = CssNamedColorProposal(color)
            store.append(proposal)

        filter_fn = lambda proposal, data: proposal.text.startswith(data.word)
        store_filter = Gtk.CustomFilter.new(filter_fn, self._filter_data)
        task.proposals = Gtk.FilterListModel.new(store, store_filter)
        task.return_boolean(True)

    def do_populate_finish(self, result: Gio.AsyncResult) -> Gio.ListModel:
        if result.propagate_boolean():
            return result.proposals

    def do_refilter(self, context: GtkSource.CompletionContext, model: Gio.ListModel) -> None:
        word = context.get_word()
        old_word = self._filter_data.word
        change = Gtk.FilterChange.DIFFERENT
        if old_word and word.startswith(old_word):
            change = Gtk.FilterChange.MORE_STRICT
        elif old_word and old_word.startswith(word):
            change = Gtk.FilterChange.LESS_STRICT
        self._filter_data.word = word
        model.get_filter().changed(change)


class CssNamedColorProposal(GObject.Object, GtkSource.CompletionProposal):
    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class CssFunctionCompletionProvider(GObject.GObject, GtkSource.CompletionProvider):
    FUNCTIONS = [
        "hsl",
        "hsla",
        "rgb",
        "rgba",
    ]

    def __init__(self):
        super().__init__()
        self._filter_data: FilterData = FilterData()

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
        text = f"{proposal.text}()"
        buffer.insert(begin, text, len(text))
        begin.backward_char()
        buffer.place_cursor(begin)
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
        return 3

    def do_get_title(self) -> str:
        return "Functions"

    def do_populate_async(self, context, cancellable, callback, user_data=None) -> None:
        task = Gio.Task.new(self, cancellable, callback)
        store = Gio.ListStore.new(CssFunctionProposal)
        self._filter_data.word = context.get_word()

        for function in self.FUNCTIONS:
            proposal = CssFunctionProposal(function)
            store.append(proposal)

        def filter_fn(proposal, data):
            return proposal.text.startswith(data.word)

        store_filter = Gtk.CustomFilter.new(filter_fn, self._filter_data)
        task.proposals = Gtk.FilterListModel.new(store, store_filter)
        task.return_boolean(True)

    def do_populate_finish(self, result: Gio.AsyncResult) -> Gio.ListModel:
        if result.propagate_boolean():
            return result.proposals

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


class CssFunctionProposal(GObject.Object, GtkSource.CompletionProposal):
    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class CssPropertyCompletionProvider(GObject.GObject, GtkSource.CompletionProvider):
    PROPERTIES = sorted(Style.__optional_keys__)

    def __init__(self):
        super().__init__()
        self._filter_data: FilterData = FilterData()

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
        text = f"{proposal.text}: "
        buffer.insert(begin, text, len(text))
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
        return 1

    def do_get_title(self) -> str:
        return "Properties"

    def do_populate_async(self, context, cancellable, callback, user_data=None) -> None:
        task = Gio.Task.new(self, cancellable, callback)
        store = Gio.ListStore.new(CssPropertyProposal)
        self._filter_data.word = context.get_word()

        for prop in self.PROPERTIES:
            proposal = CssPropertyProposal(prop)
            store.append(proposal)

        def filter_fn(proposal, data):
            return proposal.text.startswith(data.word)

        store_filter = Gtk.CustomFilter.new(filter_fn, self._filter_data)
        task.proposals = Gtk.FilterListModel.new(store, store_filter)
        task.return_boolean(True)

    def do_populate_finish(self, result: Gio.AsyncResult) -> Gio.ListModel:
        if result.propagate_boolean():
            return result.proposals

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


class CssPropertyProposal(GObject.Object, GtkSource.CompletionProposal):
    def __init__(self, text: str):
        super().__init__()
        self.text: str = text


class FilterData:
    word: str
