# vim:sw=4
"""
Logger

Logger is a simple entry point for writing log messages.
"""

class Logger(object):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    FATAL = 5

    def __init__(self):
	self.__log_level = Logger.DEBUG

    def set_log_level(self, level):
	assert level >= Logger.DEBUG and level <= Logger.FATAL
	self.__log_level = level
	
    def log(self, level, message, exc=None):
	assert level >= Logger.DEBUG and level <= Logger.FATAL
	if level >= self.__log_level:
	    print '[Gaphor-%s]' % ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'FATAL' )[level - 1], message
	    if exc:
		print '[Gaphor-Exception]', exc

    def debug(self, message, exc=None):
	self.log(Logger.DEBUG, message, exc)

    def info(self, message, exc=None):
	self.log(Logger.INFO, message, exc)

    def warning(self, message, exc=None):
	self.log(Logger.WARNING, message, exc)

    def error(self, message, exc=None):
	self.log(Logger.ERROR, message, exc)

    def fatal(self, message, exc=None):
	self.log(Logger.FATAL, message, exc)

