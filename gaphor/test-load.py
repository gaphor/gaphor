import UML
import tree
import ui
import gtk
print 'Importing diagram'
import diagram
print 'Importing diagram... done'

factory = UML.ElementFactory ()
factory.load('a.xml')
treemodel = tree.NamespaceModel(factory.lookup(1))

treemodel.dump()

dia = factory.lookup(2)
assert isinstance(dia, diagram.Diagram)

view = ui.DiagramView(dia)

view.window.connect ('destroy', lambda x: gtk.main_quit())

gtk.main()
