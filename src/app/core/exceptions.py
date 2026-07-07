class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class SlugAlreadyExistsError(Exception):
    pass


class SlugNotFoundError(Exception):
    pass


class InvalidTokenError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class PermissionDeniedError(Exception):
    pass


class ClickNotFoundError(Exception):
    pass
