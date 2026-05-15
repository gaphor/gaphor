# Systems Modeling Language v2

```{important}
The implementation for SysML v2 support is ongoing. The code is not stable
and suitable for day-to-day use.
```

We provide you a heads-up (or teaser if you like) on our work to implement
SysML version 2. SysML v2 provides

Where SysML v1 was build on top of UML, version 2 is completely rebuild from
the ground up to be a _Systems_ Modeling language, not an extension of UML.
As a result we also had to rethink how we build and support data models in
Gaphor. For this new language, we choose to use the offical specification
(XMI file) as the basis for the model. For the language specification, please
consult the official specification at https://www.omg.org/spec/SysML.

By default, SysML v2 is disabled in Gaphor. If you want to experiment, or
contribute, you can enable it by setting the environment variable
`GAPHOR_FEATURE_FLAG`:

```bash
GAPHOR_FEATURE_FLAG=sysml2 gaphor
```

More information on this new modeling language can be found at the OMG:
https://www.omg.org/sysml/sysmlv2/.


## Roadmap

- [x] Bootstrap the modeling language
- [x] Generate the KerML and SysML v2 models from XMI
- [ ] Support derive- constraints for subsets
- [x] Support for SysML v2 constructs in the Model Browser
- [ ] Diagram support (model elements and toolbox)
- [ ] Support check- and validate- constraints for model verification


## Implementation

Gaphor has the concept of a [Modeling Language](../modeling_language.md)
baked into the application
for a long time. That's how Gaphor is able to distinguish UML, SysML, RAAML,
and C4. For SysML v2 we have to bring it one step further. While SysML,
RAAML and C4 are all based upon UML, SysML v2 is a completely different
language. At first glance there seems to be some overlap in base classes
(`Element`, `Namespace`), but their implementation is different.

We've been preparing the implementation of SysML2 for a while already.
The biggest change is that UML is no longer _the_ base modeling language.
As a result all code related to _any_ modeling language had to be moved
into the package for their respected language. Modeling elements are now
namespaced by their language.
This helps when languages have similar element names (e.g. `Dependency` is
defined for both UML and C4).
