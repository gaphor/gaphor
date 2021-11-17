from __future__ import annotations

import functools
import logging
from pathlib import Path

import sphinx.util.docutils
from docutils import nodes

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.plugins.diagramexport import DiagramExport
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage import storage

# TODO: How to know a model has changed and we should regenerate images?

logger = logging.getLogger(__name__)


def setup(app: sphinx.application.Sphinx) -> dict[str, object]:
    """Called by Sphinx to set up the extension."""
    app.add_config_value("gaphor_models", {}, "env", [dict])

    app.add_directive("diagram", DiagramDirective)

    app.connect("config-inited", config_inited)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def config_inited(app, config):
    logger.info(f"Gaphor models: {str(config.gaphor_models)}")
    if isinstance(config.gaphor_models, str):
        config.gaphor_models = {"default": config.gaphor_models}


class DiagramDirective(sphinx.util.docutils.SphinxDirective):
    """The "``..

    diagram::``" directive.
    """

    has_content = False
    required_arguments = 1
    final_argument_whitespace = True

    # optional arguments: model name
    # width/height/alt

    def run(self) -> list[nodes.Node]:
        name = self.arguments[0]

        model_file = self.config.gaphor_models.get("default")

        if not model_file:
            return [nodes.paragraph(text=f"No diagram {name} in model {model_file}")]

        model = load_model(model_file)
        outdir = Path(self.env.app.doctreedir).relative_to(Path.cwd()) / ".." / "gaphor"
        outdir.mkdir(exist_ok=True)

        # TODO: find by qualified name

        # find by name

        diagram = next(
            model.select(lambda e: isinstance(e, Diagram) and e.name == name)
        )

        DiagramExport().save_svg(outdir / f"{diagram.id}.svg", diagram)

        return [
            nodes.paragraph(text=f"Diagram placeholder for {name}, {model_file}"),
            nodes.image(
                rawsource=self.block_text,
                uri=str(outdir / f"{diagram.id}.svg"),
                **self.options,
            ),
        ]


@functools.lru_cache(maxsize=None)
def load_model(model_file: str) -> ElementFactory:
    element_factory = ElementFactory()
    storage.load(
        model_file,
        element_factory,
        modeling_language=ModelingLanguageService(EventManager()),
    )
    return element_factory
