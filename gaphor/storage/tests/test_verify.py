from gaphor.storage.verify import orphan_references
from gaphor import UML
from gaphor.services.eventmanager import EventManager


def test_verifier():
    factory = UML.ElementFactory(EventManager())
    c = factory.create(UML.Class)
    p = factory.create(UML.Property)
    c.ownedAttribute = p

    assert not orphan_references(factory)

    # Now create a separate item, not part of the factory:

    m = UML.Comment(id="acd123")
    m.annotatedElement = c
    assert m in c.ownedComment

    assert orphan_references(factory)
