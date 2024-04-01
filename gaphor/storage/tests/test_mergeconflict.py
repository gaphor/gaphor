import io

import pytest
from dulwich.repo import Repo

from gaphor.storage.mergeconflict import split_ours_and_theirs
from gaphor.storage.tests.fixtures import create_merge_conflict


@pytest.mark.filterwarnings("ignore:use .* Repo._get_user_identity:DeprecationWarning")
def test_split_git_repo(tmp_path):
    repo = Repo.init(tmp_path)
    filename = "testfile.txt"
    test_file = tmp_path / filename

    create_merge_conflict(
        repo,
        test_file,
        initial_text="Initial commit",
        our_text="Second commit",
        their_text="Branch commit",
    )

    ancestor = io.BytesIO()
    ours = io.BytesIO()
    theirs = io.BytesIO()
    result = split_ours_and_theirs(test_file, ancestor, ours, theirs)

    assert result
    assert ancestor.getbuffer() == b"Initial commit"
    assert ours.getbuffer() == b"Second commit"
    assert theirs.getbuffer() == b"Branch commit"
