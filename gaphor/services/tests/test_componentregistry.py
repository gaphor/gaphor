from gaphor.services.componentregistry import ComponentRegistry


class Dependency:
    pass


def test_no_services_for_partial_service_application():
    component_registry = ComponentRegistry()
    dependency = Dependency()
    component_registry.register("dependency", dependency)

    class TestSubject:
        def __init__(self, myarg):
            self.myarg = myarg

    subject = component_registry.partial(TestSubject)(1)

    assert subject.myarg == 1


def test_partial_service_application():
    component_registry = ComponentRegistry()
    dependency = Dependency()
    component_registry.register("dependency", dependency)

    class TestSubject:
        def __init__(self, dependency):
            self.dependency = dependency

    subject = component_registry.partial(TestSubject)()

    assert subject.dependency is dependency
