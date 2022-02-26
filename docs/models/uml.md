# Unified Modeling Language

The UML model is the most extensive model in Gaphor.
It is used as a base language for [SysML](sysml.md),
[RAAML](raaml.md), and [C4](c4model.md).

Gaphor follows the [official UML 2.5.1 data model](https://www.omg.org/spec/UML/).
Where changes have been made a comment has been added to the model.
In particular where _m:n_ relationships subset _1:n_ relationships.

```{diagram} 00. Overview
:model: uml
```

```{toctree}
:caption: Packages
:maxdepth: 1

uml/01._Common_Structure
uml/02._Values
uml/03._Classification
uml/04._Simple_Classifiers
uml/05._Structured_Classifiers
uml/06._Packaging
uml/07._Common_Behaviors
uml/08._State_Machines
uml/09._Activities
uml/10._Actions
uml/11._Interactions
uml/12._Use_Cases
uml/13._Deployments
uml/14._Information_Flows
uml/A._Gaphor_Specific_Constructs
uml/B._Gaphor_Profile
```
