from gaphor.ui import run


def test_self_test():
    exit_code = run(["--self-test"])

    assert exit_code == 0
