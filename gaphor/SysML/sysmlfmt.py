from gaphor.core.format import format
from gaphor.i18n import gettext
from gaphor.SysML import sysml


@format.register(sysml.Allocate)
@format.register(sysml.Refine)
@format.register(sysml.Trace)
def format_directed_relationship_property_path(el):
    return gettext("sourceContext: {name}").format(
        name=el.sourceContext and el.sourceContext.name or ""
    )
