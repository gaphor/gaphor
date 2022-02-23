import os

from hypothesis import settings

from gaphor.conftest import case, test_models

settings.register_profile(
    "test", derandomize=True, max_examples=50, stateful_step_count=20
)
settings.register_profile("ci", max_examples=2000)
settings.load_profile("test")
