# vim:sw=4
"""
Logger

Logger is a simple entry point for writing log messages.
"""
import sys

class Logger(object):
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5

    def __init__(self):
	self.__log_level = Logger.DEBUG
	self.__loggers = list()

    def add_logger(self, logger):
	self.__loggers.append(logger)

    def remove_logger(self, logger):
	try:
	    self.__loggers.remove(logger)
	except:
	    pass

    def set_log_level(self, level):
	assert level >= Logger.DEBUG and level <= Logger.CRITICAL
	self.__log_level = level
	
    def get_log_level(self, level):
	return self.__log_level

    log_level = property(get_log_level, get_log_level, None, 'Log level')

    def log(self, level, message, exc=None):
	assert level >= Logger.DEBUG and level <= Logger.CRITICAL
	handled = False
	for logger in self.__loggers:
	    try:
		handled = handled or logger(level, message, exc)
	    except Exception, e:
		self.default_logger(Logger.ERROR,
			    'Could not write to logger %s: %s' % (logger, e))
	if not handled:
	    self.default_logger(level, message, exc)

    def debug(self, message, exc=None):
	self.log(Logger.DEBUG, message, exc)

    def info(self, message, exc=None):
	self.log(Logger.INFO, message, exc)

    def warning(self, message, exc=None):
	self.log(Logger.WARNING, message, exc)

    def error(self, message, exc=None):
	self.log(Logger.ERROR, message, exc)

    def critical(self, message, exc=None):
	self.log(Logger.CRITICAL, message, exc)

    def default_logger(self, level, message, exc=None):
	"""The default logger sends log information to stdout.
	"""
	if level >= self.__log_level:
	    print '[Gaphor-%s] %s' % (('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' )[level - 1], message)
	    if exc:
		print '[Gaphor-Exception]', exc

