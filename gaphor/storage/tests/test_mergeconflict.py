import io
import textwrap

from gaphor.storage.mergeconflict import split


def test_splitter():
    fd = io.BytesIO()
    fd.write(
        textwrap.dedent(
            """\
        <<<<<<< HEAD
        current line
        =======
        incoming line
        >>>>>>> 3b251489 (Move tool selection to toolbox)
        """
        ).encode("utf-8")
    )
    fd.seek(0)
    current, incoming = split(fd)

    assert current.read() == b"current line\n"
    assert incoming.read() == b"incoming line\n"


def test_splitter_windows_line_endings():
    fd = io.BytesIO()
    fd.write(
        textwrap.dedent(
            """\
        <<<<<<< HEAD\r
        current line\r
        =======\r
        incoming line\r
        >>>>>>> 3b251489 (Move tool selection to toolbox)\r
        """
        ).encode("utf-8")
    )
    fd.seek(0)
    current, incoming = split(fd)

    assert current.read() == b"current line\r\n"
    assert incoming.read() == b"incoming line\r\n"


def test_split_with_shared_content():
    fd = io.BytesIO()
    fd.write(
        textwrap.dedent(
            """\
        shared line
        <<<<<<< HEAD
        current line
        =======
        incoming line
        >>>>>>> 3b251489 (Move tool selection to toolbox)
        shared line
        """
        ).encode("utf-8")
    )
    fd.seek(0)
    current, incoming = split(fd)

    assert current.read() == b"shared line\ncurrent line\nshared line\n"
    assert incoming.read() == b"shared line\nincoming line\nshared line\n"


def test_no_merge_conflict():
    fd = io.BytesIO()
    fd.write(
        textwrap.dedent(
            """\
        current line
        """
        ).encode("utf-8")
    )
    fd.seek(0)
    current, incoming = split(fd)

    assert current.read() == b"current line\n"
    assert not incoming
