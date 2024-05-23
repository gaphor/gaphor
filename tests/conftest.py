# ruff: noqa: F401

from hypothesis import settings

from gaphor.conftest import (
    create,
    diagram,
    element_factory,
    event_manager,
    modeling_language,
    test_models,
    tmp_get_cache_config_dir,
)

settings.register_profile(
    "test", derandomize=True, max_examples=10, stateful_step_count=100
)
settings.register_profile("ci", max_examples=1000)
settings.load_profile("test")
