# vim:sw=4

class DiagramItem(object):
    """
    Basic functionality for all model elements (lines and elements!).

    This class contains common functionallity for model elements and
    relationships.
    """

    def __init__(self):
	self.__subject = None
	self.connect ('notify::parent', DiagramItem.on_parent_notify)

    def get_subject(self):
	"""Get the subject that is represented by this diagram item."""
	return self.__subject

    def set_subject(self, subject):
	"""Set a subject."""
	self.set_property('subject', subject)
	#self._set_subject(subject)

    def _set_subject(self, subject):
	"""Real (protected) set_subject method. Should be called by
	do_set_property(), in the sub-classes.
	"""
	if subject is not self.__subject:
	    if self.__subject:
		self.__subject.disconnect(self.on_subject_update)
		self.__subject.remove_presentation(self)
	    self.__subject = subject
	    if subject:
		subject.add_presentation(self)
		subject.connect(self.on_subject_update)

    # Define subject property:
    subject = property (get_subject, set_subject, None, 'Subject')

    def save_property(self, save_func, name):
	'''Save a property, this is a shorthand method.'''
	save_func(name, self.get_property(name))

    # DiaCanvasItem callbacks
    def _on_glue(self, handle, wx, wy, parent):
	if handle.owner.allow_connect_handle (handle, self):
	    #print self.__class__.__name__, 'Glueing allowed.'
	    return parent.on_glue (self, handle, wx, wy)
	#else:
	    #print self.__class__.__name__, 'Glueing NOT allowed.'
	# Dummy value with large distance value
	return None

    def _on_connect_handle (self, handle, parent):
	if handle.owner.allow_connect_handle (handle, self):
	    #print self.__class__.__name__, 'Connection allowed.'
	    ret = parent.on_connect_handle (self, handle)
	    if ret != 0:
		handle.owner.confirm_connect_handle(handle)
		return ret
	#else:
	    #print self.__class__.__name__, 'Connection NOT allowed.'
	return 0

    def _on_disconnect_handle (self, handle, parent):
	if handle.owner.allow_disconnect_handle (handle):
	    #print self.__class__.__name__, 'Disconnecting allowed.'
	    ret = parent.on_disconnect_handle (self, handle)
	    if ret != 0:
		handle.owner.confirm_disconnect_handle(handle, self)
		return ret
	#else:
	    #print self.__class__.__name__, 'Disconnecting NOT allowed.'
	return 0

    def on_parent_notify (self, parent):
	if self.__subject:
	    if self.parent:
		#print 'Have Parent', self, parent
		self.__subject.add_presentation (self)
	    else:
		#print 'No parent...', self, parent
		self.__subject.remove_presentation (self)

    def on_subject_update (self, name, old_value, new_value):
	pass
	#log.debug('DiagramItem: unhandled signal "%s"' % str(name))
