import io
import textwrap

import pygit2

from gaphor.storage.mergeconflict import split, split_ours_and_theirs
from gaphor.storage.tests.fixtures import create_merge_conflict


def test_split_git_repo(tmp_path):
    repo = pygit2.init_repository(tmp_path)
    filename = "testfile.txt"
    test_file = tmp_path / filename

    create_merge_conflict(
        repo,
        test_file,
        initial_text="Initial commit",
        our_text="Second commit",
        their_text="Branch commit",
    )

    ours = io.StringIO()
    theirs = io.StringIO()
    result = split_ours_and_theirs(test_file, ours, theirs)

    assert result
    assert ours.getvalue() == "Second commit"
    assert theirs.getvalue() == "Branch commit"


def test_splitter():
    fd = io.StringIO()
    fd.write(
        textwrap.dedent(
            """\
        <<<<<<< HEAD
        current line
        =======
        incoming line
        >>>>>>> 3b251489 (Move tool selection to toolbox)
        """
        )
    )
    fd.seek(0)
    current = io.StringIO()
    incoming = io.StringIO()
    split(fd, current, incoming)

    assert current.read() == "current line\n"
    assert incoming.read() == "incoming line\n"


def test_splitter_windows_line_endings():
    fd = io.StringIO()
    fd.write(
        textwrap.dedent(
            """\
        <<<<<<< HEAD\r
        current line\r
        =======\r
        incoming line\r
        >>>>>>> 3b251489 (Move tool selection to toolbox)\r
        """
        )
    )
    fd.seek(0)
    current = io.StringIO()
    incoming = io.StringIO()
    split(fd, current, incoming)

    assert current.read() == "current line\r\n"
    assert incoming.read() == "incoming line\r\n"


def test_split_with_shared_content():
    fd = io.StringIO()
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
        )
    )
    fd.seek(0)
    current = io.StringIO()
    incoming = io.StringIO()
    split(fd, current, incoming)

    assert current.read() == "shared line\ncurrent line\nshared line\n"
    assert incoming.read() == "shared line\nincoming line\nshared line\n"


def test_no_merge_conflict():
    fd = io.StringIO()
    fd.write(
        textwrap.dedent(
            """\
        current line
        """
        )
    )
    fd.seek(0)
    current = io.StringIO()
    incoming = io.StringIO()

    split(fd, current, incoming)

    assert current.read() == "current line\n"
    assert incoming.closed
