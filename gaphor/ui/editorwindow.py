#!/usr/bin/env python
# vim: sw=4:et

import sys
import gtk
import gaphor
from abstractwindow import AbstractWindow

_WELCOME_TEXT = """Welcome in Gaphor's Editor!

Here you can create small scripts.
The following modules are already
imported:
gaphor - Gaphor package
UML - UML data model (gaphor.UML)
ui - User interface stuff (gaphor.ui)
diagram - Diagram items (gaphor.diagram)
misc - utility package (gaphor.misc)

For convenience, the ElementFactory resource
has been added as 'element_factory'.
---
"""

class EditorWindow(AbstractWindow):
    
    menu = ('_File', (
                'EditorRun',
                'separator',
                'FileClose'),
            '_Edit', (
                'EditorClear',),
            )
    toolbar = ('EditorRun', 'separator', 'EditorClear')

    def __init__(self):
        AbstractWindow.__init__(self)
        # Set up local variables for execution
        import gaphor
        import gaphor.UML
        import gaphor.ui
        import gaphor.misc
        import gaphor.diagram
        self.__locals = {
            'gaphor': gaphor,
            'UML': gaphor.UML,
            'ui': gaphor.ui,
            'misc': gaphor.misc,
            'diagram': gaphor.diagram,
            'element_factory': gaphor.resource('ElementFactory'),
            'clear': self.clear_results
        }

    def get_source_text_view(self):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        return self.source

    def get_result_text_view(self):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        return self.result

    def construct(self):
        paned = gtk.VPaned()
        
        source = gtk.TextView()
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolled_window.add(source)
        paned.pack1(scrolled_window, resize=True)

        result = gtk.TextView()
        result.set_editable(0)
        result.set_wrap_mode(gtk.WRAP_CHAR)
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        scrolled_window.add(result)
        paned.pack2(scrolled_window, resize=True)
        tb = result.get_buffer()
        tb.insert(tb.get_end_iter(), _WELCOME_TEXT)
        
        self.source = source
        self.result = result
        paned.show_all()

        self._construct_window(name='editor',
                               title='Gaphor Editor',
                               size=(400, 400),
                               contents=paned)

    def run(self):
        self._check_state(AbstractWindow.STATE_ACTIVE)
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        result_buf = self.get_result_text_view().get_buffer()
        sys.stdout = PseudoFile(result_buf, 'stdout')
        sys.stderr = PseudoFile(result_buf, 'stderr')
        try:
            text_buf = self.get_source_text_view().get_buffer()
            text = text_buf.get_text (text_buf.get_start_iter(),
                                          text_buf.get_end_iter(), 0)

            code = None
            try:
                code = compile(text + '\n', '<input>', 'exec')
            except (SyntaxError, OverflowError, ValueError):
                print 'Error'
            if code:
                exec code in self.__locals
        except Exception, e:
            import traceback
            print 'ERROR: ',
            traceback.print_exc()
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

    def clear_results(self):
        """Clear the results text buffer."""
        self._check_state(AbstractWindow.STATE_ACTIVE)
        tb = self.result.get_buffer()
        tb.delete(tb.get_start_iter(), tb.get_end_iter())

    def _on_window_destroy(self, window):
        AbstractWindow._on_window_destroy(self, window)
        del self.source
        del self.result


class PseudoFile:

    def __init__(self, text_buffer, tags):
        self.text_buffer = text_buffer
        self.tags = tags

    def write(self, s):
        #self.shell.write(s, self.tags)
        try:
            tb = self.text_buffer
            tb.insert(tb.get_end_iter(), s)
        except Exception, e:
            pass
        while gtk.events_pending():
            gtk.main_iteration(False)

    def writelines(self, l):
        map(self.write, l)

    def flush(self):
        pass

    def isatty(self):
        return 1

import editoractions

