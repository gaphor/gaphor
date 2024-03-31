from gaphor.diagram.diagramtoolbox import DiagramType
from gaphor.diagram.general.diagramitem import DiagramItem
from gaphor.diagram.group import change_owner
from gaphor.diagram.support import represents
from gaphor.i18n import gettext
from gaphor.SysML.sysml import SysMLDiagram

represents(SysMLDiagram)(DiagramItem)


class DiagramDefault:
    def __init__(self, from_type, to_type, name):
        self.from_type = from_type
        self.to_type = to_type
        self.name = name


class SysMLDiagramType(DiagramType):
    def __init__(self, id, name, sections, allowed_types=(), defaults=()):
        super().__init__(id, name, sections)
        self._allowed_types = allowed_types
        assert all(d.to_type in allowed_types for d in defaults)
        self._defaults = defaults

    def allowed(self, element) -> bool:
        if isinstance(element, self._allowed_types):
            return True

        return any(isinstance(element, d.from_type) for d in self._defaults)

    def create(self, element_factory, element):
        if not isinstance(element, self._allowed_types):
            try:
                d = next(d for d in self._defaults if isinstance(element, d.from_type))
                assert d.to_type in self._allowed_types
                new_element = element_factory.create(d.to_type)
                new_element.name = d.name
                if element:
                    change_owner(element, new_element)
                element = new_element
            except StopIteration as si:
                raise TypeError(
                    gettext("Can’t create “{name}” nested under a “{elem}”").format(
                        name=self.name, elem=element.name
                    )
                ) from si

        diagram = element_factory.create(SysMLDiagram)
        diagram.name = diagram.gettext(self.name)
        diagram.diagramType = self.id
        if element:
            change_owner(element, diagram)

        return diagram
