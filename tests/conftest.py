# ruff: noqa: F401

import os

from hypothesis import Phase, settings

from gaphor.conftest import (
    assert_not_in_transaction,
    create,
    diagram,
    element_factory,
    event_manager,
    modeling_language,
    test_models,
    tmp_get_cache_config_dir,
)

settings.register_profile(
    "test",
    derandomize=True,
    max_examples=10,
    stateful_step_count=100,
    deadline=20000,
    phases=[Phase.generate],
)
settings.register_profile("ci", max_examples=1000)
settings.load_profile("test")
