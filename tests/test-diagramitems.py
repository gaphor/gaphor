# vim:sw=4:et:ai

import unittest
from weakref import ref as wref
from sys import getrefcount
import gaphor.UML as UML
import gaphor.diagram as diagram

factory = UML.ElementFactory()

class TestDiagramItems(unittest.TestCase):

    def gc_collect(self):
        import gc
        for x in range(6): gc.collect()

    def _testTemplate1(self, uml_class, item_class):
        m = factory.create(UML.Package)
        d = factory.create(UML.Diagram)
        d.package = m
        p1 = factory.create(uml_class)
        p1.package = m
        pi1 = d.create(item_class)
        pi1.subject = p1
        w_m = wref(m)
        w_d = wref(d)
        w_p1 = wref(p1)
        w_pi1 = wref(pi1)
        del m, d, p1, pi1
        factory.flush()
        self.gc_collect()
        self.assertEquals(w_m(), None)
        self.failUnless(w_d() is None)
        self.failUnless(w_p1() is None)
        self.failUnless(w_pi1() is None)

    def _testTemplate2(self, uml_class, item_class):
        m = factory.create(UML.Package)
        d = factory.create(UML.Diagram)
        d.package = m
        p1 = factory.create(uml_class)
        p1.package = m
        pi1 = d.create(item_class)
        pi1.subject = p1
        rc_p1 = getrefcount(p1)
        rc_pi1 = getrefcount(pi1)
        p2 = factory.create(uml_class)
        p2.package = m
        pi2 = d.create(item_class)
        pi2.subject = p2
        self.assertEquals(getrefcount(p1), rc_p1)
        self.assertEquals(getrefcount(pi1), rc_pi1)
        d.canvas.update_now()
        self.assertEquals(getrefcount(p1), rc_p1)
        self.assertEquals(getrefcount(pi1), rc_pi1)
        w_m = wref(m)
        w_d = wref(d)
        w_p1 = wref(p1)
        w_pi1 = wref(pi1)
        w_p2 = wref(p2)
        w_pi2 = wref(pi2)
        self.assertEquals(getrefcount(p1), rc_p1)
        self.assertEquals(getrefcount(pi1), rc_pi1)
        del m, d, p1, pi1, p2, pi2
        self.assertEquals(getrefcount(w_p1()), rc_p1 - 1)
        self.assertEquals(getrefcount(w_pi1()), rc_pi1 - 1)
        factory.flush()
        self.gc_collect()
        self.failUnless(w_p1() is None, getrefcount(w_p1()))
        self.failUnless(w_pi1() is None, getrefcount(w_p1()))
        self.failUnless(w_p2() is None, getrefcount(w_p1()))
        self.failUnless(w_pi2() is None, getrefcount(w_p1()))
        self.failUnless(w_m() is None, getrefcount(w_p1()))
        self.failUnless(w_d() is None, getrefcount(w_p1()))

    def testPackage1(self):
        self._testTemplate1(UML.Package, diagram.PackageItem)

    def testPackage2(self):
        self._testTemplate2(UML.Package, diagram.PackageItem)

    def testClass1(self):
        self._testTemplate1(UML.Class, diagram.ClassItem)

    def testClass2(self):
        self._testTemplate2(UML.Class, diagram.ClassItem)

    def testDependency1(self):
        self._testTemplate1(UML.Dependency, diagram.DependencyItem)

    def testDependency2(self):
        self._testTemplate2(UML.Dependency, diagram.DependencyItem)

    def _testTemplate3(self, uml_class, item_class):
        import gtk
        import gaphor.ui as ui
        m = factory.create(UML.Package)
        d = factory.create(UML.Diagram)
        d.package = m
        p1 = factory.create(uml_class)
        p1.package = m
        pi1 = d.create(item_class)
        pi1.subject = p1
        rc_p1 = getrefcount(p1)
        rc_pi1 = getrefcount(pi1)
        p2 = factory.create(uml_class)
        p2.package = m
        pi2 = d.create(item_class)
        pi2.subject = p2
        self.assertEquals(getrefcount(p1), rc_p1)
        self.assertEquals(getrefcount(pi1), rc_pi1)
        d.canvas.update_now()
        win = gtk.Window()
        view = ui.DiagramView(d)
        win.add(view)
        win.show_all()
        win.destroy()
        self.assertEquals(getrefcount(p1), rc_p1)
        self.assertEquals(getrefcount(pi1), rc_pi1)
        w_m = wref(m)
        w_d = wref(d)
        w_p1 = wref(p1)
        w_pi1 = wref(pi1)
        w_p2 = wref(p2)
        w_pi2 = wref(pi2)
        self.assertEquals(getrefcount(p1), rc_p1)
        self.assertEquals(getrefcount(pi1), rc_pi1)
        del m, d, p1, pi1, p2, pi2
        del win, view
        self.assertEquals(getrefcount(w_p1()), rc_p1 - 1)
        self.assertEquals(getrefcount(w_pi1()), rc_pi1 - 1)
        factory.flush()
        self.gc_collect()
        self.failUnless(w_p1() is None, getrefcount(w_p1()))
        self.failUnless(w_pi1() is None, getrefcount(w_p1()))
        self.failUnless(w_p2() is None, getrefcount(w_p1()))
        self.failUnless(w_pi2() is None, getrefcount(w_p1()))
        self.failUnless(w_m() is None, getrefcount(w_p1()))
        self.failUnless(w_d() is None, getrefcount(w_p1()))

    def testSubjectNotify(self):
        """Test the working of the DiagramItem.on_subject_notify().
        """
        p1 = factory.create(UML.Package)
        p2 = factory.create(UML.Package)
        c = factory.create(UML.Class)
        d = factory.create(UML.Diagram)
        self.failUnless(getrefcount(c) == 3, getrefcount(c))
        ci = d.create(diagram.ClassItem)

        # Add the class to the item
        #c.package = p1
        ci.subject = c
        self.failUnless(len(c._observers['appliedStereotype']) == 1,
                        c._observers['appliedStereotype'])
        self.failUnless(len(c._observers['isAbstract']) == 1,
                        c._observers['isAbstract'])
        self.failUnless(len(c._observers['namespace']) == 2,
                        c._observers['namespace'])
        self.failUnless(len(c._observers['ownedOperation']) == 1,
                        c._observers['ownedOperation'])
        self.failUnless(len(c._observers['ownedAttribute']) == 1,
                        c._observers['ownedAttribute'])
        
        # Change the package:
        #print '\n\nPhase 2:'
        c.package = p1
        self.failUnless(len(c._observers['namespace']) == 2,
                        c._observers['namespace'])
        self.failUnless(len(p1._observers.get('name', [])) == 1,
                        p1._observers.get('name'))

        #print '\n\nPhase 3:'
        c.package = p2
        self.failUnless(len(c._observers['namespace']) == 2,
                        c._observers['namespace'])
        self.failUnless(len(p1._observers.get('name', [])) == 0,
                        p1._observers.get('name'))
        self.failUnless(len(p2._observers.get('name', [])) == 1,
                        p2._observers.get('name'))

        ci.subject = None
        # Note: does a __unlink__ on all elements -> c.package = None
        self.failUnless(len(c._observers['namespace']) == 0,
                        c._observers['namespace'])
        self.failUnless(len(p1._observers.get('name', [])) == 0,
                        p1._observers.get('name'))
        self.failUnless(len(p2._observers.get('name', [])) == 0,
                        p2._observers.get('name'))
        
        #print '\nLast:'
        c.package = p2
        ci.subject = c
        self.failUnless(len(c._observers['namespace']) == 2,
                        c._observers['namespace'])
        self.failUnless(len(p1._observers.get('name', [])) == 0,
                        p1._observers.get('name'))
        self.failUnless(len(p2._observers.get('name', [])) == 1,
                        p2._observers.get('name'))
        
if __name__ == '__main__':
    unittest.main()

