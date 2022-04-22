from gaphor.UML.actions.pin import InputPinItem


def test_load_pin(element_factory, diagram, saver, loader):
    attached = diagram.create(InputPinItem)

    attached.handles()[0].pos = (1, 2)
    attached.matrix.translate(10, 20)

    dump = saver()
    loader(dump)

    new_attached = next(element_factory.select(InputPinItem))

    assert tuple(map(float, new_attached.handles()[0].pos)) == (1, 2)
    assert tuple(new_attached.matrix) == (1.0, 0.0, 0.0, 1.0, 10, 20)
