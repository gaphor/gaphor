from gaphor import UML


def test_qualified_name():
    p1 = UML.Package()
    p2 = UML.Package()
    p3 = UML.Package()

    p1.name = "package1"
    p2.name = "package2"
    p3.name = "package3"
    p3.package = p2
    p2.package = p1

    assert p3.qualifiedName == ["package1", "package2", "package3"]
