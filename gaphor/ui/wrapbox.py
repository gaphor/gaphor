#vim:sw=4:et

import pygtk
pygtk.require('2.0')
import gobject
import gtk


class WrapBox(object):

    def __init__(self):
        self.resize_idle_id = 0
        self.rows = 1
        self.cols = 0
        self.table = gtk.Table(self.rows, self.cols)
        self.table.connect('size_allocate', self.on_size_allocate)
        self.children = []

    def calculate_size(self, allocation):
        children = self.children
        max_width = 0
        for c in children:
            size_request = c.size_request()
            #print size_request
            max_width = max(max_width, size_request[0])
        cols = allocation.width / max_width
        if cols == 0:
            cols = 1
        rows = len(children) / cols
        if len(children) % cols:
            rows += 1
        return cols, rows

    def set_new_size(self):
        table = self.table
        children = self.children
        rows = self.rows
        cols = self.cols
        for c in children:
            table.remove(c)
        table.resize(rows, cols)
        x = y = 0
        for c in children:
            table.attach(c, left_attach=x, right_attach=x+1, top_attach=y, bottom_attach=y+1)
            x += 1
            if x  == rows:
                x = 0
                y += 1

    def _idle_handler(self):
	try:
	    self.set_new_size()
	finally:
	    self.resize_idle_id = 0

    def on_size_allocate(self, table, allocation):
        rows, cols = self.calculate_size(allocation)
        #print 'size_allocate', rows, cols
        if not self.resize_idle_id and (rows != self.rows or cols != self.cols):
            #print 'size_allocate', 'setting idle handler'
            self.resize_idle_id = gobject.idle_add(self._idle_handler)
        self.rows = rows
        self.cols = cols

    def add(self, widget):
        self.cols += 1
        row = self.rows
        col = self.cols
        self.table.attach(widget, left_attach=col-1, right_attach=col,
                          top_attach=row-1, bottom_attach=row)
        self.children.append(widget)


if __name__ == '__main__':
    def make_wrapbox(button_labels):
        wrapbox = WrapBox()
        for label in button_labels:
            b = gtk.Button(label)
            wrapbox.add(b)
        return wrapbox.table

        table = gtk.Table(len(button_labels), 1)
        i = 0
        for label in button_labels:
            b = gtk.Button(label)
            table.attach(b, left_attach=i, right_attach=i+1, top_attach=0, bottom_attach=1)
            i += 1
        table.connect('size_allocate', on_size_allocate)
        #table.connect('size_request', on_size_allocate)
        return table

    def on_toggled(button, content):
        arrow = button.get_children()[0]
        if button.get_property('active'):
            content.show()
            arrow.set(gtk.ARROW_DOWN, gtk.SHADOW_IN)
        else:
            content.hide()
            arrow.set(gtk.ARROW_RIGHT, gtk.SHADOW_IN)

    def make(content, expanded=False):
        hbox = gtk.HBox()
        vbox = gtk.VBox()

        vbox.add(hbox)

        button = gtk.ToggleButton()

        arrow = gtk.Arrow(gtk.ARROW_RIGHT, gtk.SHADOW_IN)
        button.add(arrow)
        hbox.pack_start(button, False, False, 0)

        label = gtk.Label('Classes')

        hbox.pack_start(label, expand=False, fill=True)
        vbox.show_all()

        button.connect('toggled', on_toggled, content)

        vbox.pack_start(content, True, True)
        
        vbox.label = label
        vbox.content = content

        button.set_property('active', expanded)
        on_toggled(button, content)
        return vbox
    win = gtk.Window()
    button_labels=('1','2','3','4','5','6','7')
    content = make(make_wrapbox(button_labels))
    paned = gtk.HPaned()
    paned.pack1(content)
    paned.pack2(gtk.Button('x'))
    paned.show()
    win.add(paned)

    win.connect('destroy', lambda e: gtk.mainquit())
    win.show_all()

    gtk.main()
