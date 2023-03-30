# Resolve Merge Conflicts

Suppose you’re working on a model. If you create a change, while someone else has
also made changes, there’s a fair chance you'll end up with a merge conflict.

Gaphor tries to make the changes to a model as small as possible: all elements are
stored in the same order. However, since a Gaphor model is a persisted graph of objects,
merging changes is not as simple as opening a text editor.

From Gaphor 2.18 onwards Gaphor is also capable of merging models.
Once a merge conflict has been detected, Gaphor will offer the option to open the current model,
the incoming model or merge changes manually via the Merge Editor.

![merge dialog](images/merge-dialog.png)

If you choose *Open Merge Editor*, both models will be loaded and the differences will be calculated.
The differences are added to the model, so you can save the file and continue merge conflict resolution
at a later point.

The Merge Editor is shown on the right side, replacing the (normal) element editor.

![merge conflict window](images/merge-conflict-window.png)

Merge actions are grouped by diagram, where possible.
Once changes are applied, they can only be reverted by undoing the change (hit _Undo_).

```{note}
If you accept all changes, you’ll end up with the incoming model.
```

When all conflicts have been resolved, press *Resolve* to finish merge conflict resolution.
