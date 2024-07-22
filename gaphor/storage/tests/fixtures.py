import subprocess

import pytest
from dulwich import porcelain
from dulwich.repo import Repo


def create_merge_conflict(repo: Repo, filename, initial_text, our_text, their_text):
    def commit_all(message):
        porcelain.add(repo, paths=[filename])
        return porcelain.commit(
            repo, author=b"Alice Author <alice@gaphor.org>", message=message
        )

    filename.write_text(initial_text, encoding="utf-8")
    main_ref = commit_all("Initial commit")

    porcelain.branch_create(repo, "branch")
    porcelain.checkout_branch(repo, "branch")
    filename.write_text(their_text, encoding="utf-8")
    branch_oid = commit_all("Branch commit")

    porcelain.checkout_branch(repo, main_ref)
    filename.write_text(our_text, encoding="utf-8")
    commit_all("Second commit")

    # `porcelain.merge` function does not exist.
    _porcelain_merge(repo, branch_oid)


def _porcelain_merge(repo, branch):
    """Merge branch with git cli."""

    subprocess.run(
        ["git", "config", "user.name", "Alice Author"], cwd=repo.path, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "alice@gaphor.org"], cwd=repo.path, check=True
    )
    with pytest.raises(subprocess.CalledProcessError):
        subprocess.run(["git", "merge", branch], cwd=repo.path, check=True)
