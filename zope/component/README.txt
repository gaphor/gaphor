Zope Component Architecture
===========================

This package, together with `zope.interface`, provides facilities for
defining, registering and looking up components.  There are two basic
kinds of components: adapters and utilities.

Utilities
---------

Utilities are just components that provide an interface and that are
looked up by an interface and a name.  Let's look at a trivial utility
definition:

    >>> from zope import interface

    >>> class IGreeter(interface.Interface):
    ...     def greet():
    ...         "say hello"

    >>> class Greeter:
    ...     interface.implements(IGreeter)
    ...
    ...     def __init__(self, other="world"):
    ...         self.other = other
    ...
    ...     def greet(self):
    ...         print "Hello", self.other

We can register an instance this class using `provideUtility` [1]_:

    >>> from zope import component
    >>> greet = Greeter('bob')
    >>> component.provideUtility(greet, IGreeter, 'robert')

In this example we registered the utility as providing the `IGreeter`
interface with a name of 'bob'. We can look the interface up with
either `queryUtility` or `getUtility`:

    >>> component.queryUtility(IGreeter, 'robert').greet()
    Hello bob

    >>> component.getUtility(IGreeter, 'robert').greet()
    Hello bob

`queryUtility` and `getUtility` differ in how failed lookups are handled:

    >>> component.queryUtility(IGreeter, 'ted')
    >>> component.queryUtility(IGreeter, 'ted', 42)
    42
    >>> component.getUtility(IGreeter, 'ted')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ComponentLookupError: (<InterfaceClass ...IGreeter>, 'ted')

If a component provides only one interface, as in the example above,
then we can omit the provided interface from the call to `provideUtility`:

    >>> ted = Greeter('ted')
    >>> component.provideUtility(ted, name='ted')
    >>> component.queryUtility(IGreeter, 'ted').greet()
    Hello ted

The name defaults to an empty string:

    >>> world = Greeter()
    >>> component.provideUtility(world)
    >>> component.queryUtility(IGreeter).greet()
    Hello world

Adapters
--------

Adapters are components that are computed from other components to
adapt them to some interface.  Because they are computed from other
objects, they are provided as factories, usually classes.  Here, we'll
create a greeter for persons, so we can provide personalized greetings
for different people:

    >>> class IPerson(interface.Interface):
    ...     name = interface.Attribute("Name")

    >>> class PersonGreeter:
    ...
    ...     component.adapts(IPerson)
    ...     interface.implements(IGreeter)
    ...
    ...     def __init__(self, person):
    ...         self.person = person
    ...
    ...     def greet(self):
    ...         print "Hello", self.person.name

The class defines a constructor that takes an argument for every
object adapted.

We used `component.adapts` to declare what we adapt.  We can find
out if an object declares that it adapts anything using adaptedBy:

    >>> list(component.adaptedBy(PersonGreeter)) == [IPerson]
    True

If an object makes no declaration, then None is returned:

    >>> component.adaptedBy(Greeter()) is None
    True


If we declare the interfaces adapted and if we provide only one
interface, as in the example above, then we can provide the adapter
very simply [1]_:

    >>> component.provideAdapter(PersonGreeter)

For adapters that adapt a single interface to a single interface
without a name, we can get the adapter by simply calling the
interface:

    >>> class Person:
    ...     interface.implements(IPerson)
    ...
    ...     def __init__(self, name):
    ...         self.name = name

    >>> IGreeter(Person("Sally")).greet()
    Hello Sally

We can also provide arguments to be very specific about what
how to register the adapter.

    >>> class BobPersonGreeter(PersonGreeter):
    ...     name = 'Bob'
    ...     def greet(self):
    ...         print "Hello", self.person.name, "my name is", self.name

    >>> component.provideAdapter(
    ...                        BobPersonGreeter, [IPerson], IGreeter, 'bob')

The arguments can also be provided as keyword arguments:

    >>> class TedPersonGreeter(BobPersonGreeter):
    ...     name = "Ted"

    >>> component.provideAdapter(
    ...     factory=TedPersonGreeter, adapts=[IPerson],
    ...     provides=IGreeter, name='ted')

For named adapters, use `queryAdapter`, or `getAdapter`:

    >>> component.queryAdapter(Person("Sally"), IGreeter, 'bob').greet()
    Hello Sally my name is Bob

    >>> component.getAdapter(Person("Sally"), IGreeter, 'ted').greet()
    Hello Sally my name is Ted

If an adapter can't be found, `queryAdapter` returns a default value
and `getAdapter` raises an error:

    >>> component.queryAdapter(Person("Sally"), IGreeter, 'frank')
    >>> component.queryAdapter(Person("Sally"), IGreeter, 'frank', 42)
    42
    >>> component.getAdapter(Person("Sally"), IGreeter, 'frank')
    ... # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    ComponentLookupError: (...Person...>, <...IGreeter>, 'frank')

Adapters can adapt multiple objects:

    >>> class TwoPersonGreeter:
    ...
    ...     component.adapts(IPerson, IPerson)
    ...     interface.implements(IGreeter)
    ...
    ...     def __init__(self, person, greeter):
    ...         self.person = person
    ...         self.greeter = greeter
    ...
    ...     def greet(self):
    ...         print "Hello", self.person.name
    ...         print "my name is", self.greeter.name

    >>> component.provideAdapter(TwoPersonGreeter)

To look up a multi-adapter, use either `queryMultiAdapter` or
`getMultiAdapter`:

    >>> component.queryMultiAdapter((Person("Sally"), Person("Bob")),
    ...                                  IGreeter).greet()
    Hello Sally
    my name is Bob

Adapters need not be classes.  Any callable will do.  We use the
adapter decorator (in the Python 2.4 decorator sense) to declare that
a callable object adapts some interfaces (or classes):

    >>> class IJob(interface.Interface):
    ...     "A job"

    >>> class Job:
    ...     interface.implements(IJob)

    >>> def personJob(person):
    ...     return getattr(person, 'job', None)
    >>> personJob = interface.implementer(IJob)(personJob)
    >>> personJob = component.adapter(IPerson)(personJob)

(In Python 2.4, the example can be written::

    @interface.implementer(IJob)
    @component.adapter(IPerson)
    def personJob(person):
        return getattr(person, 'job', None)

which looks a bit nicer.)

In this example, the personJob function simply returns the person's
`job` attribute if present, or None if it's not present.  An adapter
factory can return None to indicate that adaptation wasn't possible.
Let's register this adapter and try it out:

    >>> component.provideAdapter(personJob)
    >>> sally = Person("Sally")
    >>> IJob(sally) # doctest: +ELLIPSIS
    Traceback (most recent call last):
    ...
    TypeError: ('Could not adapt', ...

The adaptation failed because sally didn't have a job.  Let's give her
one: 

    >>> job = Job()
    >>> sally.job = job
    >>> IJob(sally) is job
    True

Subscription Adapters
*********************

Unlike regular adapters, subscription adapters are used when we want
all of the adapters that adapt an object to a particular adapter.

Consider a validation problem.  We have objects and we want to assess
whether they meet some sort of standards.  We define a validation
interface:

    >>> class IValidate(interface.Interface):
    ...     def validate(ob):
    ...         """Determine whether the object is valid
    ...         
    ...         Return a string describing a validation problem.
    ...         An empty string is returned to indicate that the
    ...         object is valid.
    ...         """

Perhaps we have documents:

    >>> class IDocument(interface.Interface):
    ...     summary = interface.Attribute("Document summary")
    ...     body = interface.Attribute("Document text")

    >>> class Document:
    ...     interface.implements(IDocument)
    ...     def __init__(self, summary, body):
    ...         self.summary, self.body = summary, body

Now, we may want to specify various validation rules for
documents. For example, we might require that the summary be a single
line:

    >>> class SingleLineSummary:
    ...     component.adapts(IDocument)
    ...     interface.implements(IValidate)
    ...
    ...     def __init__(self, doc):
    ...         self.doc = doc
    ...
    ...     def validate(self):
    ...         if '\n' in self.doc.summary:
    ...             return 'Summary should only have one line'
    ...         else:
    ...             return ''

Or we might require the body to be at least 1000 characters in length:

    >>> class AdequateLength:
    ...     component.adapts(IDocument)
    ...     interface.implements(IValidate)
    ...
    ...     def __init__(self, doc):
    ...         self.doc = doc
    ...
    ...     def validate(self):
    ...         if len(self.doc.body) < 1000:
    ...             return 'too short'
    ...         else:
    ...             return ''

We can register these as subscription adapters [1]_:

    >>> component.provideSubscriptionAdapter(SingleLineSummary)
    >>> component.provideSubscriptionAdapter(AdequateLength)

We can then use the subscribers to validate objects:

    >>> doc = Document("A\nDocument", "blah")
    >>> [adapter.validate()
    ...  for adapter in component.subscribers([doc], IValidate)
    ...  if adapter.validate()]
    ['Summary should only have one line', 'too short']

    >>> doc = Document("A\nDocument", "blah" * 1000)
    >>> [adapter.validate()
    ...  for adapter in component.subscribers([doc], IValidate)
    ...  if adapter.validate()]
    ['Summary should only have one line']

    >>> doc = Document("A Document", "blah")
    >>> [adapter.validate()
    ...  for adapter in component.subscribers([doc], IValidate)
    ...  if adapter.validate()]
    ['too short']

Handlers
********

Handlers are subscription adapter factories that don't produce
anything.  They do all of their work when called.  Handlers
are typically used to handle events.

Event subscribers are different from other subscription adapters in
that the caller of event subscribers doesn't expect to interact with
them in any direct way.  For example, an event publisher doesn't
expect to get any return value.  Because subscribers don't need to
provide an API to their callers, it is more natural to define them
with functions, rather than classes.  For example, in a
document-management system, we might want to record creation times for
documents:

    >>> import datetime

    >>> def documentCreated(event):
    ...     event.doc.created = datetime.datetime.utcnow()

In this example, we have a function that takes an event and performs
some processing.  It doesn't actually return anything.  This is a
special case of a subscription adapter that adapts an event to
nothing.  All of the work is done when the adapter "factory" is
called.  We call subscribers that don't actually create anything
"handlers".  There are special APIs for registering and calling
them.

To register the subscriber above, we define a document-created event: 

    >>> class IDocumentCreated(interface.Interface):
    ...     doc = interface.Attribute("The document that was created")

    >>> class DocumentCreated:
    ...     interface.implements(IDocumentCreated)
    ...
    ...     def __init__(self, doc):
    ...         self.doc = doc

We'll also change our handler definition to:

    >>> def documentCreated(event):
    ...     event.doc.created = datetime.datetime.utcnow()

    >>> documentCreated = component.adapter(IDocumentCreated)(documentCreated)

(Note that in Python 2.4, this can be written:

     @component.adapter(IDocumentCreated)
     def documentCreated(event):
         event.doc.created = datetime.datetime.utcnow()
)

This marks the handler as an adapter of `IDocumentCreated` events.

Now we'll register the handler  [1]_:

    >>> component.provideHandler(documentCreated)

Now, if we can create an event and use the `handle` function to call
handlers registered for the event:

    >>> component.handle(DocumentCreated(doc))
    >>> doc.created.__class__.__name__
    'datetime'



.. [1] CAUTION: This API should only be used from test or
       application-setup code. This API shouldn't be used by regular
       library modules, as component registration is a configuration
       activity.
