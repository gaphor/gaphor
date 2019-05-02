Event system
============

Generic library provides ``generic.event`` module which helps you implement
event systems in your application. By event system I mean an API for
*subscribing* for some types of events and to *fire* those events so previously
subscribed *handlers* are being executed.

.. contents::
   :local:

Basic usage
-----------

First you need to describe event types you want to use in your application,
``generic.event`` dispatches events to corresponding handlers by inspecting
events' types, so it's natural to model those as classes::

  class CommentAdded(object):
    def __init__(self, post_id, comment):
      self.post_id = post_id
      self.comment = comment

Now you want to register handler for your event type::

  from generic.event import subscriber

  @subscriber(CommentAdded)
  def print_comment(ev):
    print "Got new comment: %s" % ev.comment

Then you just call ``generic.event.fire`` function with ``CommentAdded``
instance as its argument::

  from generic.event import fire

  fire(CommentAdded(167, "Hello!")) # prints `Got new comment: Hello!`

This is how it works.

Event inheritance
-----------------

Using per-application event API
-------------------------------

API reference
-------------

.. autoclass:: generic.event.Manager
   :members: subscribe, subscriber, fire, unsubscribe

Functions below are just aliases for methods of globally instantiated
manager:

.. autofunction:: generic.event.subscribe(handler, event_type)
.. autofunction:: generic.event.subscriber(event_type)
.. autofunction:: generic.event.fire(event)
.. autofunction:: generic.event.unsubscribe(handler, event_type)
