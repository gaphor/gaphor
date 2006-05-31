# vim:sw=4:et

#from distutils.dist import Distribution as _Distribution
from distutils.core import Distribution as _Distribution

class Distribution(_Distribution):

    def __init__(self, attrs=None):
        if attrs and attrs.has_key('all_linguas'):
            self.all_linguas = attrs['all_linguas']
            del attrs['all_linguas']
        _Distribution.__init__(self, attrs)

    def get_all_linguas(self):
        return self.all_linguas or []

