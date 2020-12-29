from gaphor.plugins.console.console import docstring_dedent


def test_docstring_with_leading_space():
    docstr = """\
        line one
        line two
        """

    expected = "line one\nline two\n"

    assert docstring_dedent(docstr) == expected


def test_docstring_without_leading_space():
    docstr = """line one
        line two
        """

    expected = "line one\nline two\n"

    assert docstring_dedent(docstr) == expected


def test_docstring_without_leading_space_with_blank_line():
    docstr = """line one

        line two
        """

    expected = "line one\n\nline two\n"

    assert docstring_dedent(docstr) == expected
