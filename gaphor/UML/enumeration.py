
class Enumeration_:
    '''The Enumerration class is an abstract class that can be used to create
    enumerated types. One should inherit from Enumeration and define a variable
    '_values' at class level, which holds a list of valid values for the class.
    '''
    def __init__(self):
        self.v = self._values[0]
    def __setattr__(self, key, value):
        if key == 'v' and value in self._values:
	    self.__dict__['v'] = value
	else:
	    raise AttributeError, "Value '" + str(value) + "' is an invalid enumeration type."

