# Event System

The Generic library provides the `generic.event` module which is used to
implement the event system in Gaphor. This event system in Gaphor provides an
API to *subscribe* to events and to then *handle* those events so previously
subscribed *handlers* are being executed.

## Basic Usage

In order to specify the event types we want to use in Gaphor, `generic.event`
dispatches events to corresponding handlers by inspecting the events' types. We
represent the even types as a class:

```Python
class CommentAdded:
    def __init__(self, post_id, comment):
      self.post_id = post_id
      self.comment = comment
```

Next we register a handler for your event type:

    from gaphor.misc.generic.event import subscriber

    @subscriber(CommentAdded)
    def print_comment(ev):
        print(f"Got new comment: {ev.comment}")

Finally call `generic.event.handle` function with `CommentAdded` instance as
its argument, in order to execute the subscribed handler to print the comment:

    from gaphor.misc.generic.event import handle

    handle(CommentAdded(167, "Hello!"))  # prints `Got new comment: Hello!`

## API Reference

```eval_rst
.. autoclass:: gaphor.misc.generic.event.Manager
```
