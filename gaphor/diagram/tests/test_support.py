from gaphor.diagram.support import closest_instance


def test_closest_instance():
    class A:
        pass

    class B:
        pass

    class C(A):
        pass

    class D(A):
        pass

    class E(B):
        pass

    class F(E):
        pass

    assert closest_instance(A, (A, B, C, D)) is A
    assert closest_instance(F, (A, B, C, D)) is B
    assert closest_instance(C, (A, B, C, D)) is C
