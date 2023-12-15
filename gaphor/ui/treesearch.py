import functools
from typing import Iterable
from unicodedata import normalize

from gaphor.ui.treemodel import TreeItem, tree_item_sort

"""
Inputs:

1. Text changing
   -> return first match from start_tree_item
2. "next"
   -> return first match from start_tree_item
      update start_tree_item

3. selected item changed
 - change not due to 1. or 2.
 - start search from this element in case of 1 and 2
4. model changed (elements added/removed)
 - only important in case 1 and 2
"""


def search(search_text, tree_walker: Iterable[TreeItem]):
    search_text = normalize("NFC", search_text).casefold()

    for tree_item in tree_walker:
        text = normalize("NFC", tree_item.readonly_text).casefold()
        if tree_item.element and search_text in text:
            return tree_item


def sorted_tree_walker(
    model, start_tree_item=None, from_current=False
) -> Iterable[TreeItem]:
    """The tree model as one stream, sorted."""

    def _flatten(list_store):
        for tree_item in sorted_tree_items(list_store):
            yield tree_item
            if children := model.child_model(tree_item):
                yield from _flatten(children)

    iterator = _flatten(model.root)

    if start_tree_item:
        for tree_item in iterator:
            if tree_item is start_tree_item:
                if from_current:
                    yield tree_item
                break

    yield from iterator

    # Do not cache, to avoid stale data
    if start_tree_item:
        for tree_item in _flatten(model.root):
            yield tree_item
            if tree_item is start_tree_item:
                break


def sorted_tree_items(branch):
    return sorted(
        branch,
        key=functools.cmp_to_key(tree_item_sort),
    )
