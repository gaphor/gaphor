from exceptiongroup import ExceptionGroup


class raises_exception_group:
    def __init__(
        self,
        expected_exception,
    ) -> None:
        self.expected_exception = expected_exception

    def __enter__(self):
        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> bool:
        if not issubclass(exc_type, ExceptionGroup):
            return False

        return any(
            isinstance(exc, self.expected_exception) for exc in exc_val.exceptions
        )
