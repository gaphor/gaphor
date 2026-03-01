"""Tests for template loading from external files."""

from gaphor.plugins.htmlreport.templates import (
    CSS_TEMPLATE,
    HTML_TEMPLATE,
    JS_TEMPLATE,
)


def test_html_template_has_placeholders():
    assert "{css}" in HTML_TEMPLATE
    assert "{model_data}" in HTML_TEMPLATE
    assert "{js}" in HTML_TEMPLATE


def test_css_template_is_non_empty():
    assert len(CSS_TEMPLATE) > 0
    assert "body" in CSS_TEMPLATE


def test_js_template_is_non_empty():
    assert len(JS_TEMPLATE) > 0
    assert "MODEL_DATA" in JS_TEMPLATE


def test_html_template_includes_svg_pan_zoom_cdn():
    assert "svg-pan-zoom" in HTML_TEMPLATE
