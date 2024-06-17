from gaphor.settings import get_cache_dir, get_config_dir


def test_config_dir():
    config_dir = get_config_dir()
    assert str(config_dir).endswith("gaphor")


def test_cache_dir():
    cache_dir = get_cache_dir()
    assert str(cache_dir).endswith("gaphor")
