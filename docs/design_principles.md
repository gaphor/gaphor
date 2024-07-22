# Design Principles

Gaphor has been around for quite a few years. In those years we (the Gaphor
developers) learned a few things on how to build it. Gaphor tries to be easily
accessible for novice users as well as a useful tool for more experienced users.

Gaphor is not your average editor. It's a modeling environment. This implies
there is a language underpinning the models. Languages adhere to rules and
Gaphor tries to follow those rules.

Usability is very important. When you're new to Gaphor, it should be easy
to find your way around. Minimal knowledge of UML should at least allow you to
create a class diagram.

```{diagram} Design Principles
:model: design-principles
```

## Guidance

To help users, Gaphor should provide guidance where it can.

### Help with relationships

The diagram has a feature that it grays out all elements a relationship can not
connect to. This helps you to decide where a relation can connect to. You can
still mix different elements, but we try to make it as simple as possible to
make consistent models.

### Keep the model in sync

An important part of modeling is to design a system in abstractions and be
able to explain those to others. As systems become more complicated, it's
important to have the design (model) layed out in diagrams.

Gaphor goes through great lengths to keep the model in sync with the diagrams.
In doing so, unused elements can be automatically removed from the model if
they're no longer shown in any diagram.

## Out of your way

When modeling, you should be busy with your problem or solution domain, not with
the tool. Gaphor tries to stay out of your way as much as possible. It does not
try to nag you with error messages, because the model is not "correct".

### Avoid dialogs

In doing the right thing, and staying out of the way of users, Gaphor avoids the
use of dialogs as much as possible.

Gaphor should allow you to do the sensible thing (see above) and not get you out
of your flow with all sorts of questions.

### Notify on changes

When Gaphor is doing something that is not directly visible, you'll see a
notification, for example, an element that's indirectly removed from the model.
It will not interrupt you with dialogs, but only provide a small in-app
notification. If the change is undesired, hit `undo`.

### Balanced

Although Gaphor implements quite a bit of the UML 2 model, it's not complete.
We try to find the right balance in features to suite both expert and novice
modellers.

## Continuity

A model that is created should be usable in the future. Gaphor does acknowledge
that. We care about compatibility.

### Backwards compatibility

Gaphor is capable of loading models going back to Gaphor 1.0. It's important for
a tool to always allow older models to be loaded.

### Multi-platform

We put a lot of effort in making Gaphor run on all major platforms: Windows,
macOS, and Linux. Having Gaphor available on all platforms is essential if the
model needs to be shared. It would be awful if you need to run one specific
operating system in order to open a model.

So far, we do not support the fourth major platform (web). Native applications
provide a better user experience (once installed). But this may change.

## User interaction

Gaphor is originally written on Linux. It uses [GTK](https://gtk.org) as it's
user interface toolkit. This sort of implies that Gaphor follows the [GNOME
Human Interface Guidelines (HIG)](https://developer.gnome.org/hig/). Gaphor is
also a multi-platform application. We try to stay close to the GNOME HIG, but
try not to introduce concepts that are not available on Windows and macOS.

User interface components are not generated. We found that UI generation (like
many enterprise modeling tools do) provides an awful user experience. We want users
to use Gaphor on a regular basis, so we aim for it to be a tool that's
pleasant to look at and easy to work with.


## What else?

On a technical level, the following principles are also applicable:

* **Idempotency** Allow the same operation to be applied multiple times. This should
  not affect the result.
* **Event Driven** Gaphor is a user application. It acts to user events. The application
  uses an internal event dispatches (event bus) to distribute events to interested parties.
  Everyone should be able to listen to events.
