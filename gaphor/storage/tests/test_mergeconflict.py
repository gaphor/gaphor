import io
import textwrap

import pygit2

from gaphor.storage.mergeconflict import split, split_ours_and_theirs


def test_split_git_repo(tmp_path):
    repo = pygit2.init_repository(tmp_path)
    filename = "testfile.txt"
    test_file = tmp_path / filename

    create_merge_conflict(
        repo,
        test_file,
        initial_text="Initial commit",
        second_text="Second commit",
        branch_text="Branch commit",
    )

    ours, theirs = split_ours_and_theirs(test_file)

    assert ours == b"Second commit"
    assert theirs == b"Branch commit"


def create_merge_conflict(repo, filename, initial_text, second_text, branch_text):
    def commit_all(message, parents):
        ref = "HEAD"
        author = pygit2.Signature("Alice Author", "alice@gaphor.org")

        index = repo.index
        index.add_all()
        index.write()
        tree = index.write_tree()

        return repo.create_commit(ref, author, author, message, tree, parents)

    filename.write_text(initial_text)
    initial_oid = commit_all("Initial commit", parents=[])
    main_ref = repo.head
    branch_ref = repo.references.create("refs/heads/branch", initial_oid)

    repo.checkout(branch_ref)
    filename.write_text(branch_text)
    branch_oid = commit_all("Branch commit", parents=[initial_oid])

    repo.checkout(main_ref)
    filename.write_text(second_text)
    commit_all("Second commit", parents=[initial_oid])

    repo.merge(branch_oid)


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
