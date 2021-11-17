import sphinx.application
import sphinx.util.docutils

from gaphor.sphinx import setup as sphinx_setup


def test_setup(tmp_path):
    gen = sphinx.application.Sphinx(
        srcdir="docs",
        confdir="docs",
        outdir=tmp_path,
        doctreedir=tmp_path,
        buildername="html",
    )

    result = sphinx_setup(gen)

    assert result["version"] == "0.1"
    assert result["parallel_read_safe"]
    assert result["parallel_write_safe"]

    assert sphinx.util.docutils.is_directive_registered("diagram")
    assert gen.config.gaphor_models == {}


def test_setup_load_models(tmp_path):
    (tmp_path / "conf.py").write_text(
        "gaphor_models = {'style-sheets': 'style-sheet-examples.gaphor'}"
    )
    gen = sphinx.application.Sphinx(
        srcdir="docs",
        confdir=tmp_path,
        outdir=tmp_path,
        doctreedir=tmp_path,
        buildername="html",
    )

    result = sphinx_setup(gen)

    assert result["version"] == "0.1"
    assert result["parallel_read_safe"]
    assert result["parallel_write_safe"]

    assert sphinx.util.docutils.is_directive_registered("diagram")
