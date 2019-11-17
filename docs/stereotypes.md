# Stereotypes

UML defines a concept called a stereotype, which is how you can extend an
existing metaclass. This allows you to create new notation that can add to or
replace existing elements. In order to create a stereotype in Gaphor, first you
need to create a Profile. A profile is a collection of stereotypes. Next a
Diagram can be created within the profile. Although a diagram in Gaphor can
accept any type of element, by convention, the profile diagram should only
contain items that are useful within a profile:

-   Classes, which will function as a `<<metaclass>>`.
-   Stereotype, which will be defined as `<<stereotype>>`.
-   Extensions, connecting metaclasses and stereotypes.

Comment, Association, Generalization, and Dependency can also be used within a
profile diagram, just like other UML diagrams.

Some things to keep in mind when working with profiles:

- Profiles are reusable and its common to share them across different models.
- A stereotype can only be owned by a profile, it can not be in a normal
  Package.
- In order to make use of a stereotype, Gaphor has to perform a lookup if the
  MetaClass it is extended from is part of the model.
- A stereotype can contain an image, which can be used instead of its name.
- Profiles should be saved with the model too. It should also be possible to
  "update" a profile within a model.
- Stereotypes that you define should be instantiated in your model when you
  create a stereotyped class.

``` note:: There is no way to connect a stereotype with a class other than an Association.
```
