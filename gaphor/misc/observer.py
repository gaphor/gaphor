# vim:sw=4

class Observer(object):
    def __init__(self):
        pass
                        
    def update(self, subject):  
        pass               
                
class Subject(object):
    def __init__(self):        
        self._observers = list()
        
    def attach(self, observer): 
	if not self._observers.index(observer):
	    self._observers.append(observer)
        
    def detach(self, observer): 
        try:
            self._observers.remove(observer)
        except:
            pass
            
    def notify(self, modifier=None):
	"""
	Send updates to the connected objects. modifier is the class that
	did the update (so doesn't need to be notified).
	"""
        for observer in self._observers:            
            if modifier != observer:
                observer.update(self)

