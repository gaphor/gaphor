from gaphor.ui import main


def test_self_test():
    exit_code = main(["--self-test"])

    assert exit_code == 0
