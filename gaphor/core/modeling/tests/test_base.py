from gaphor.core.modeling.base import Base

__modeling_language__ = "test"


class A(Base):
    pass


def test_modeling_language():
    assert Base.__modeling_language__ == "Core"
    assert A.__modeling_language__ == "test"
