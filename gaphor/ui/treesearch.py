import functools
from unicodedata import normalize

from gaphor.ui.treemodel import TreeItem, tree_item_sort


def search(model, search_text, start_tree_item=None):
    search_text = normalize("NFC", search_text).casefold()

    have_match = True
    while have_match:
        have_match = False
        model_iterator = flatten_tree_model(model, start_tree_item)

        for tree_item in model_iterator:
            text = normalize("NFC", tree_item.text).casefold()
            if search_text in text:
                have_match = True
                cmd = yield tree_item
                if isinstance(cmd, str):
                    search_text = normalize("NFC", cmd).casefold()
                elif isinstance(cmd, TreeItem):
                    start_tree_item = cmd
                    break


def flatten_tree_model(model, start_tree_item):
    """The tree model as one steam, sorted."""

    def _flatten(list_store):
        for tree_item in sorted_tree_items(list_store):
            yield tree_item
            if children := model.child_model(tree_item):
                yield from _flatten(children)

    cache = []

    iterator = _flatten(model.root)
    if start_tree_item:
        for tree_item in iterator:
            if tree_item is start_tree_item:
                # yield start_tree_item
                break
            cache.append(tree_item)

    yield from iterator
    yield from cache


def sorted_tree_items(list_store):
    return sorted(
        (list_store.get_item(n) for n in range(list_store.get_n_items())),
        key=functools.cmp_to_key(tree_item_sort),
    )
