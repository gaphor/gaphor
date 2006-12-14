"""
Logger

Logger is a simple entry point for writing log messages.

It wraps the logging module and adds some basic configuration.
"""

import logging


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s')
                    #format='%(asctime)s %(module)s:%(lineno)s %(levelname)s %(message)s')
                    #filename='/tmp/myapp.log',
                    #filemode='w')


class Logger(object):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL

    def __init__(self):
        self.logger = logging.getLogger('')

    def set_log_level(self, level):
        self.logger.setLevel(level)
        
    def get_log_level(self, level):
        return self.logger.getEffectiveLevel()

    log_level = property(get_log_level, get_log_level, None, 'Log level')

    def log(self, level, message, exc=None):
	self.logger.log(level, message, exc_info=exc)

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


# vim:sw=4
