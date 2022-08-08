ERROR_MESSAGE_ACTIVATION_DUPLICATED = (
    "Can not add a snake/ladder that shares head/bottom with another snake/ladder"
)
ERROR_MESSAGE_ACTIVATION_CLASH = (
    "Can not add a snake/ladder that starts where another ends"
)
ERROR_MESSAGE_UNSUPPORTED_ARTEFACT = (
    "Neither snake, nor ladder! Unsupported game object"
)


class EXCEPTION_ARTEFACT_INVALID_POSITION(Exception):
    message = "{artefact_type} extends outside the range of the board"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_ARTEFACT_LONG(Exception):
    message = "{artefact_type} spans the entire board"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_ARTEFACT_SHORT(Exception):
    message = "Length of the {artefact_type} must span at least one row"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_ARTEFACT_INVERSE(Exception):
    message = "{artefact_type} is inverse"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_SNAKE_AT_WINNING_POSITION(Exception):
    message = "Snake is at winning position"

    def __init__(self):
        super().__init__(self.message)


def get_user_friendly_error_message(
    artefact_type, exception, top, bottom
):  # pragma: no coverage
    exception_message = exception.message.format(artefact_type=artefact_type)
    full_message = f"Invalid {artefact_type} ({top},{bottom}): {exception_message}"
    return full_message
