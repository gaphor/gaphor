# vim:sw=4

class AbstractWindow(object):
    """
    AbstractWindow is an abstract base class for window shell related classes.
    The actual windows are created by the WindowFactory. The methods defined
    here should be overriden in window shell implementations
    """

    def get_name(self):
    	return 'New window'

    def get_title(self):
	return '***'

    def get_default_size(self):
	return (50, 50)

    def create_contents(self):
	return None

    def get_ui_xml_file(self):
	return None

