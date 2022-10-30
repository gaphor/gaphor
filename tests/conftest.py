from hypothesis import settings

from gaphor.conftest import test_models

settings.register_profile(
    "test", derandomize=True, max_examples=10, stateful_step_count=100
)
settings.register_profile("ci", max_examples=4000)
settings.load_profile("test")
