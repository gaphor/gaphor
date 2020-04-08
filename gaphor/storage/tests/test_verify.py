from gaphor import UML
from gaphor.core.modeling import ElementFactory
from gaphor.services.eventmanager import EventManager
from gaphor.storage.verify import orphan_references


def test_verifier():
    factory = ElementFactory(EventManager())
    c = factory.create(UML.Class)
    p = factory.create(UML.Property)
    c.ownedAttribute = p

    assert not orphan_references(factory)

    # Now create a separate item, not part of the factory:

    m = UML.Comment(id="acd123")
    m.annotatedElement = c
    assert m in c.ownedComment

    assert orphan_references(factory)
