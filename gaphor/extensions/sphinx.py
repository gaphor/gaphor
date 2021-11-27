from __future__ import annotations

import functools
from pathlib import Path

import sphinx.util.docutils
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives import images
from sphinx.ext.autodoc.mock import mock
from sphinx.util import logging

from gaphor.core.eventmanager import EventManager
from gaphor.core.modeling import Diagram, ElementFactory
from gaphor.diagram.export import save_pdf, save_svg
from gaphor.i18n import gettext
from gaphor.services.modelinglanguage import ModelingLanguageService
from gaphor.storage import storage

log = logging.getLogger(__name__)


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
    log.info(f"Gaphor models: {config.gaphor_models}")
    if isinstance(config.gaphor_models, str):
        config.gaphor_models = {"default": config.gaphor_models}


class DiagramDirective(sphinx.util.docutils.SphinxDirective):
    """The Gaphor diagram directive.

    Usage: "``.. diagram:: diagram-name``".
    """

    has_content = False
    required_arguments = 1
    final_argument_whitespace = True
    option_spec = {
        "model": directives.unchanged,
        **images.Image.option_spec,
    }

    def run(self) -> list[nodes.Node]:
        name = self.arguments[0]
        model_name = self.options.get("model", "default")
        model_file = self.config.gaphor_models.get(model_name)

        if not model_file:
            return self.logging_error_node(
                gettext("No model file configured for model '{model_name}'.").format(
                    model_name=model_name
                )
            )

        self.env.note_dependency(model_file)
        model = load_model(Path(self.env.srcdir) / model_file)

        outdir = (
            (Path(self.env.app.doctreedir) / ".." / "gaphor")
            .resolve()
            .relative_to(self.env.srcdir)
        )
        outdir.mkdir(exist_ok=True)

        diagram = next(
            model.select(
                lambda e: isinstance(e, Diagram) and ".".join(e.qualifiedName) == name
            ),
            None,
        )

        if not diagram:
            diagram = next(
                model.select(lambda e: isinstance(e, Diagram) and e.name == name), None
            )

        if not diagram:
            return self.logging_error_node(
                gettext(
                    "No diagram '{name}' in model '{model_name}' ({model_file})."
                ).format(name=name, model_name=model_name, model_file=model_file)
            )

        outfile = outdir / f"{diagram.id}"
        save_svg(outfile.with_suffix(".svg"), diagram)
        save_pdf(outfile.with_suffix(".pdf"), diagram)

        # Image needs a relative path. Make our outfile path relative to the doc
        for _ in Path(self.env.docname).parts[:-1]:
            outfile = Path("..") / outfile

        return [
            nodes.image(
                rawsource=self.block_text,
                uri=str(outfile) + ".*",
                **self.options,
            ),
        ]

    def logging_error_node(self, text: str) -> list[nodes.Node]:
        location = self.state_machine.get_source_and_line(self.lineno)
        log.error(text, location=location)
        return [nodes.error("", nodes.paragraph(text=text))]


@functools.lru_cache(maxsize=None)
def load_model(model_file: str) -> ElementFactory:
    element_factory = ElementFactory()

    with mock(["gi.repository.Gtk", "gi.repository.Gdk"]):
        modeling_language = ModelingLanguageService(EventManager())

    storage.load(
        model_file,
        element_factory,
        modeling_language,
    )
    return element_factory
