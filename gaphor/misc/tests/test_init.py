from gaphor.misc import get_config_dir


def test_config_dir():
    config_dir = get_config_dir()

    assert config_dir.endswith("gaphor")
