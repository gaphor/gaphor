
import pygtk
pygtk.require('2.0')
from gaphor.misc import wrapbox
import gtk

window = gtk.Window()
window.set_resizable(True)
window.set_size_request(1,1)

wrap_box = wrapbox.HWrapBox()

window.add(wrap_box)

for x in range(25):
    b = gtk.Button(str(x))
    #wrap_box.pack(b) #, False, False, False, False)
    wrap_box.pack(b, False, False, False, False)

window.show_all()

gtk.main()
