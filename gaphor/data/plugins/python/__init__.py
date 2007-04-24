"""a python import/export plugin for gaphor, based on Logilab's astng package
"""

__author__ = "Logilab"
__revision__ = "$Id$"

import sys
import os
from os.path import join, exists, isdir

from gtk import FileSelection

from gaphor import plugin, UML
from gaphor.core import inject

from logilab.common.astng import astng, raw_building as builder, inspector, \
     utils, manager


class PythonReloadAction(plugin.Action):
    
    plugin_manager = inject('plugin_manager')

    def execute(self):
        reload(astng)
        reload(builder)
        reload(manager)
        reload(inspector)
        self.plugin_manager.plugins['Python generator'].import_plugin()


class PythonExportAction(plugin.Action):

    element_factory = inject('element_factory')

    def __init__(self):
        plugin.Action.__init__(self)
        self._latest_dir = os.getcwd()
        
    def execute(self):
        """gaphor's plugin main callback"""
        dlg = FileSelection(self._latest_dir)
        dlg.set_title('Choose the directory where python code should be generated')
        dlg.cancel_button.connect_object("clicked", lambda x: x.destroy(), dlg)
        dlg.ok_button.connect_object('clicked', self.export, dlg)
        dlg.show_all()
        dlg.hide_fileop_buttons()
        dlg.file_list.parent.hide()
        dlg.run()

    def export(self, selector):
        """generate python code for the current gaphor model"""
        directory = selector.get_filename()
        self._latest_dir = directory
        selector.destroy()
        print '**** generating to python code in %s' % directory
        pyconverter.reset(directory)
        # FIXME: should we export the root package ?
        pyconverter.visit(root(self.element_factory))
        print '**** done'


class PythonImportAction(plugin.Action):
    
    element_factory = inject('element_factory')

    def execute(self):
        """gaphor's plugin main callback"""
        dlg = FileSelection()
        dlg.set_title('Choose the python module or package to import')
        dlg.cancel_button.connect_object("clicked", lambda x: x.destroy(), dlg)
        dlg.ok_button.connect_object('clicked', self.import_, dlg)
        dlg.show_all()
        dlg.hide_fileop_buttons()
        dlg.run()

    def import_(self, selector):
        filepath = selector.get_filename()
        selector.destroy()
        print '**** importing from python code in %s' % filepath
        astng_manager = manager.ASTNGManager()
        if isdir(filepath):
            module = astng_manager.from_directory(filepath)
        else:
            module = astng_manager.astng_from_file(filepath)
        linker = inspector.Linker(module, tag=1)
        linker.visit(module)
        fact = self.element_factory
        root_package = root(fact)
        gapconverter.reset(fact, module)
        root_package.nestedPackage = gapconverter.visit(module)
        print '**** done'


def root(factory):
    """return the root package element from the gaphor elements factory"""
    roots = [elmt for elmt in factory._elements.values()
             if isinstance(elmt, UML.Package) and elmt.namespace is None]
    #assert len(roots) == 1, roots
    return roots[0]

def path(elmt):
    """return the path to this gaphor element from the root package"""
    if elmt.namespace is None:
        return [elmt.name]
    return path(elmt.namespace) + [elmt.name]


class Astng2Gaphor:
    """translate a astng tree intro a gaphor UML"""
    
    def reset(self, factory, imported):
        """method to call before each import of python code to
        initialize internal structures
        """
        #print 'FACTORY', factory
        self._fact = factory
        self._root = imported
        self._uids = {}
        
    def visit(self, elmt):
        """generic visit method, dispatching to other methods according
        to the element's class
        """
        cb = getattr(self, 'visit_%s' % elmt.__class__.__name__.lower())
        return cb(elmt)

    def visit_package(self, elmt):
        try:
            return self._uids[elmt.uid]
        except:
            pass
        package = self._fact.create(UML.Package)
        self._uids[elmt.uid] = package
        package.name = elmt.name
        for subelmt in elmt.values():
            if isinstance(subelmt, astng.Module) and \
                   subelmt.name.endswith('.__init__'):
                self.visit_module(subelmt, package)
            else:
                package.nestedPackage = self.visit(subelmt)
        return package
    
    def visit_module(self, elmt, module=None):
        if module is None:
            try:
                return self._uids[elmt.uid]
            except:
                pass
            module = self._fact.create(UML.Package)
            self._uids[elmt.uid] = module
            module.name = elmt.name.split('.')[-1]
        for subelmt in elmt.locals.values():
            if isinstance(subelmt, astng.Class):
                module.ownedClassifier = self.visit_class(subelmt)
        return module

    def visit_class(self, elmt):
        try:
            return self._uids[elmt.uid]
        except:
            pass
        if utils.is_interface(elmt):
            klass = self._fact.create(UML.Interface)
        else:
            klass = self._fact.create(UML.Class)
        #print 'class id', klass.id
        self._uids[elmt.uid] = klass
        klass.name = elmt.name
        # properties
        for prop in elmt.instance_attrs.keys():
            attr = self._fact.create(UML.Property)
            attr.name = prop
            klass.ownedAttribute = attr
        # methods and class attributes
        for subelmt in elmt.locals.values():
            if isinstance(subelmt, astng.Function):
                klass.ownedOperation = self.visit_function(subelmt)
            elif isinstance(subelmt, astng.AssName) and subelmt.name != '__implements__':
                # FIXME: mark the property as class attribute
                prop = self._fact.create(UML.Property)
                prop.name = subelmt.name
                klass.ownedAttribute = prop
        # inheritance relationships
        for parent in elmt.baseobjects:
            gap_parent = self._get_related_class(parent)
            if gap_parent is None:
                continue
            generalization = self._fact.create(UML.Generalization)
            klass.generalization = generalization
            gap_parent.specialization = generalization
        # implementation relationships
        for iface in elmt.implements:
            gap_iface = self._get_related_class(iface)
            if gap_iface is None:
                continue
            implementation = self._fact.create(UML.Implementation)
            klass.implementation = implementation
        # dependancy relationship
        for related in elmt.instance_attrs_type.values():
            if not isinstance(related, astng.Class):
                continue
            related = self._get_related_class(related)
            if related is None:
                continue
            # FIXME: is Dependency the correct object class here ?
            dependency = self._fact.create(UML.Dependency)
            klass.clientDependency = dependency
            related.supplierDependency = dependency
        
        return klass
        
    def visit_function(self, elmt):
        method = self._fact.create(UML.Operation)
        method.name = elmt.name
        #print 'function argnames', elmt.argnames
        # FIXME: function parameters
        return method

    def _get_related_class(self, elmt):
        parent_modname = elmt.parent.get_frame().name 
        try:
            parent_mod = self._root.get_module('.'.join(parent_modname.split('.')[:2]))
        except KeyError, ex:
            print '%s ignored, no module %s imported' % (elmt.name, ex)
            return None
        # launch the visit on the top most parent of our parent class
        # so member / namespace relationship is correctly handled
        self.visit(parent_mod)
        # now get the gaphor element for the parent class (should be cached)
        return self.visit_class(elmt)
    
        
class Gaphor2Astng:
    """translate a gaphor UML tree to astng (i.e. object representation of
    python source code
    """
    
    def reset(self, destination_directory=None):
        """method to call before each generation of python code to
        initialize internal structures
        """
        self._uids = {}
        self._dest_dir = destination_directory or os.getcwd()

    def mk_package_dir(self, elmt):
        """compute the package directory for the given element (should
        be a Package object) and create non-existent directories on the
        path
        """
        assert isinstance(elmt, UML.Package)
        package_dir = self._dest_dir
        for directory in path(elmt):
            package_dir = join(package_dir, directory)
            if not exists(package_dir):
                os.mkdir(package_dir)
        return package_dir
    
    def visit(self, elmt):
        """generic visit method, dispatching to other methods according
        to the element's class
        """
        cb = getattr(self, 'visit_%s' % elmt.__class__.__name__.lower())
        return cb(elmt)
        
    def visit_package(self, elmt):
        """get an astng objects tree from a gaphor objects tree (starting
        from a package node)
        """
        try:
            return self._uids[elmt.id]
        except:
            pass
        # get astng module representation
        module = builder.build_module(elmt.name)
        self._uids[elmt.id] = module
        subpackages = [sub for sub in elmt.member if isinstance(sub, UML.Package)]
        subclasses = [sub for sub in elmt.member if isinstance(sub, UML.Class)]
        for member in subclasses:
	    if isinstance(member, UML.Class):
                self.visit(member)
            elif not isinstance(member, UML.Package):
                print 'ignored', elmt
        # write it to the correct location
        if subpackages:
            package_dir = self.mk_package_dir(elmt)
            stream = open(join(package_dir, '__init__.py'), 'w')
        else:
            package_dir = self.mk_package_dir(elmt.namespace)
            stream = open(join(package_dir, '%s.py' % elmt.name), 'w')
        stream.write('"""%s"""\n\n' % elmt.name)
        stream.write('__revision__ = "$Id$"\n\n')
        stream.write(module.as_string())
        stream.write('\n')
        stream.close()
        print '* %s (%s) written to %s' % (elmt.name, elmt.id, stream.name)
        # recurs on subpackages if any
        for member in subpackages:
            self.visit(member)                
        return module
    
    def visit_class(self, elmt):
        """get an astng objects tree from a gaphor objects tree (starting
        from a class node)
        """
        try:
            return self._uids[elmt.id]
        except KeyError:
            pass
        klass = builder.build_class(elmt.name)
        self._uids[elmt.id] = klass
        mymodule = self.visit(elmt.namespace)
        # handle parent classes first
        bases = []
        for gap in elmt.superClass:
            bases.append(self.visit_class(gap))
            if gap.namespace is not elmt.namespace:
                depmodule = self.visit(gap.namespace)
                # add the import if necessary
                if not gap.name in mymodule.locals:
                    import_node = builder.build_from_import(depmodule.name, (gap.name,))
                    mymodule.append_node(import_node)
                    # add imported name to module locals
                    mymodule.locals[gap.name] = import_node
        klass.set_parents([base.name for base in bases])
        # add the class node on its parent node
        mymodule.add_local_node(klass)
        # FIXME: class documentation (attached comment ?)
        function = builder.build_function('__init__', ['self'])
        for attr in elmt.ownedAttribute:
            if attr.name is None:
                # FIXME why None ?
                continue
            # FIXME: default attribute value
            klass.instance_attrs[attr] = self.visit_property(attr)
            function.append_node(klass.instance_attrs[attr])
        # add pass if empty initializer
        if not klass.instance_attrs:
            function.append_node(astng.Pass())
        klass.add_local_node(function)
        # class'methods
        for oper in elmt.ownedOperation:
            function = self.visit_operation(oper)
            function.append_node(astng.Pass())
        return klass
    
    def visit_property(self, elmt):
        """get an astng objects tree from a gaphor objects tree (starting
        from a property node)
        """
        return builder.build_attr_assign(elmt.name, None)
    
    def visit_operation(self, elmt):
        """get an astng objects tree from a gaphor objects tree (starting
        from a operation node)
        """
        parameters = [e.name for e in elmt.formalParameter]
        func = builder.build_function(elmt.name, ['self'] + parameters)
        self.visit(elmt.namespace).add_local_node(func)
        return func

        

pyconverter = Gaphor2Astng()
gapconverter = Astng2Gaphor()
