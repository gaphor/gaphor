from gaphor import UML

def pr_interface_deps(classifier, dep_type):
    """
    Return all interfaces, which are connected to a classifier with given
    dependency type.
    """
    return (dep.supplier[0] for dep in classifier.clientDependency \
        if dep.isKindOf(dep_type) and dep.supplier[0].isKindOf(UML.Interface))

def pr_rc_interface_deps(component, dep_type):
    """
    Return all interfaces, which are connected to realizing classifiers of
    specified component. Returned interfaces are connected to realizing
    classifiers with given dependency type.

    Generator of generators is returned. Do not forget to flat it later.
    """
    return (pr_interface_deps(r.realizingClassifier, dep_type) for r in component.realization)

