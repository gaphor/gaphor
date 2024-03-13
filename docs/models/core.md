# Modeling Language Core

The Core modeling language is the the basis for any other language.

The `Element` class acts as the root for all gaphor domain classes.
`Diagram` and `Presentation` form the basis for everything you see
in a diagram.

All data models in Gaphor are generated from actual Gaphor model files.
This allows us to provide you nice diagrams of Gaphor’s internal model.

```{diagram} core
:model: core
```

The {obj}`~gaphor.core.modeling.Element` base class provides event notification and integrates
with the model repository (internally known as `ElementFactory`).
Bi-directional relationships are also possible, as well as derived
relations.

## Change Sets

The core model has support for change sets, sets of pending changes.
Normally you end up with a change set when you
[resolve a merge conflict](../merge_conflicts) in your model.

This diagram is provided for completion sake.

```{diagram} change sets
:model: core
```


```{toctree}
:hidden:

core_element
```