
# vim:sw=4

class CommandInfo(object):
    __slots__ = ( 'name', '_label', 'context', '_tip', 'sensitive', 'state', 'pixtype', 'pixname', 'accel', 'command_class', 'extra_args' )

    def __init__(self, name, _label, context,
		 _tip=None, sensitive=None, state=None,
		 pixtype='stock', pixname=None,
		 accel=None, command_class=None):
	"""
	Create a new plugin command. Plugin commands are used to identify
	commands that are used throughout Gaphor. Every command should have a
	unique name and a label.
	"""
	self.name = name
	self._label = _label
	self.context = context
	self._tip = _tip
	self.sensitive = sensitive
	self.state = state
	self.pixtype = pixtype
	self.pixname = pixname
	self.accel = accel
	self.command_class = command_class

    def create_cmd_xml(self):
	xml = '<cmd name="%s" _label="%s"' % (self.name, self._label)
	if self._tip:
	    xml += ' _tip="%s"' % self._tip
	if self.sensitive:
	    xml += ' sensitive="%s"' % self.sensitive
	if self.state:
	    xml += ' state="%s"' % self.state
	if self.pixname:
	    xml += ' pixtype="%s" pixname="%s"' % (self.pixtype, self.pixname)
        if self.accel:
	    xml += ' accel="%s"' % self.accel
	xml += '/>'
	return xml

    def register(self):
	"""
	Add the CommandInfo to a hash, this should make it easely accessible.
	"""
	GaphorResource('CommandRegistry').register(self)

