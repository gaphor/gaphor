from gaphor.entrypoint import init_entrypoints


class ServiceA:
    pass


class ServiceB:
    def __init__(self, service_a, other_arg=None):
        self.service_a = service_a


class ServiceC:
    def __init__(self, service_a, service_b):
        self.service_a = service_a
        self.service_b = service_b


def test_load_single_service():
    uninitialized_services = {"service_a": ServiceA}

    initialized = init_entrypoints(uninitialized_services)

    assert "service_a" in initialized
    assert isinstance(initialized["service_a"], ServiceA)


def test_load_dependent_service():
    uninitialized_services = {"service_a": ServiceA, "service_b": ServiceB}

    initialized = init_entrypoints(uninitialized_services)

    assert "service_b" in initialized
    assert isinstance(initialized["service_b"], ServiceB)
    assert initialized["service_a"] is initialized["service_b"].service_a


def test_load_multi_dependent_service():
    uninitialized_services = {
        "service_a": ServiceA,
        "service_b": ServiceB,
        "service_c": ServiceC,
    }

    initialized = init_entrypoints(uninitialized_services)

    assert "service_c" in initialized
    assert isinstance(initialized["service_c"], ServiceC)
    assert initialized["service_a"] is initialized["service_c"].service_a
    assert initialized["service_b"] is initialized["service_c"].service_b
