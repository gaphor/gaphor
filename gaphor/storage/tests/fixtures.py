import pygit2


def create_merge_conflict(repo, filename, initial_text, our_text, their_text):
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
    filename.write_text(their_text)
    branch_oid = commit_all("Branch commit", parents=[initial_oid])

    repo.checkout(main_ref)
    filename.write_text(our_text)
    commit_all("Second commit", parents=[initial_oid])

    repo.merge(branch_oid)
