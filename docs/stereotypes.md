# Stereotypes

Stereotypes are quite another story. In order to create a stereotype one
should create a Profile. Within this profile a Diagram can be created.
This diagram should accept only items that are useful within a profile:

-   Classes, which will function as <<metaclass>>.
-   Stereotype, which will be the defined <<stereotypes>>.
-   Extensions, connecting metaclasses and stereotypes.

and of course the usual: Comment, Association, Generalization and
Dependency.

Thoughts:

-   Profiles are reusable and its common to share them with different
    models.
-   Stereotypes can only be owned by Profiles, not by (normal) Packages.
-   We have to do a lookup if a MetaClass is actually part of the model.
-   a stereotype can contain an image, that can be used instead of its
    name
-   Profiles should be saved with the model too. And it should be
    possible to \"update\" a profile within a model.

Maybe it would be nice to create Stereotypes without creating the
diagrams. Via a dialog once can select which class (Operation, Class,
etc.) is stereotyped, which extra constraints apply and/or if you
inherit from an already existing stereotype. This way it's easy to save
your stereotypes apart from the model (and possibly in the model too) so
they can be reused in other models.

I could create a special diagram window too that can be used to create
profiles. Profiles should be added to packages within the model.

This window should contain:
1. Name of the stereotype
2. Metaclass it applies to (Class, Operation, etc.)
3. If it is a subclass of an already existing metaclass
4. Constraints
5. Description
6. The profile it belongs to.

When a stereotype is used, an instance is created of the Stereotype
(meta)class. This is not really possible for our application. Gaphor
should figure out another way to do this. Should check XMI and see how
they do it (maybe a property is enough).

It looks like the stereotypes are more a concept than something that is
implementable in an application. The point is that the stereotypes you
define (instances of Stereotype) should be instantiated in your model
when you create a stereotyped class.

``` note:: There is no way to connect a stereotype with a class other than an Association.
```
