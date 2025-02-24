class UserError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnregisteredSystemConfigError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class UnregisteredSystemValueError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
