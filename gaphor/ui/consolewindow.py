#!/usr/bin/env python
# vim: sw=4

import sys
import gtk
import gaphor
from gaphor.misc.console import GTKInterpreterConsole
from abstractwindow import AbstractWindow

class ConsoleWindow(AbstractWindow):
    
    def __init__(self):
	AbstractWindow.__init__(self)

    def construct(self):
	console = GTKInterpreterConsole()

	self._construct_window(name='console',
			       title='Gaphor Console',
			       size=(400, 400),
			       contents=console,
			       params={ 'window': self })

