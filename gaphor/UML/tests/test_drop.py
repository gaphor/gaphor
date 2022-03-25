from gaphor import UML
from gaphor.diagram.drop import drop


def test_drop_class(diagram, element_factory):
    klass = element_factory.create(UML.Class)

    drop(klass, diagram, 0, 0)

    assert klass.presentation
    assert klass.presentation[0] in diagram.ownedPresentation


def test_drop_dependency(diagram, element_factory):
    client = element_factory.create(UML.Class)
    supplier = element_factory.create(UML.Class)
    dependency = element_factory.create(UML.Dependency)
    dependency.client = client
    dependency.supplier = supplier

    drop(client, diagram, 0, 0)
    drop(supplier, diagram, 0, 0)
    drop(dependency, diagram, 0, 0)
    print(element_factory.lselect())
    dep_item = dependency.presentation[0]

    assert client.presentation
    assert supplier.presentation
    assert dep_item
    assert (
        diagram.connections.get_connection(dep_item.head).connected
        is supplier.presentation[0]
    )
    assert (
        diagram.connections.get_connection(dep_item.tail).connected
        is client.presentation[0]
    )
