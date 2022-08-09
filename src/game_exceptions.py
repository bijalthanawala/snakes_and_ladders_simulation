ERROR_MESSAGE_ACTIVATION_DUPLICATED = (
    "Can not add a snake/ladder that shares head/bottom with another snake/ladder"
)
ERROR_MESSAGE_ACTIVATION_CLASH = (
    "Can not add a snake/ladder that starts where another ends"
)
ERROR_MESSAGE_UNSUPPORTED_ARTEFACT = (
    "Neither snake, nor ladder! Unsupported game object"
)


class EXCEPTION_SNAKE_LADDER_SIMULATOR(Exception):
    def __init__(self, message_fmt, artefact_type, activation_point, termination_point):
        # TODO: Check if it is a good practice to instantiate custom exception with arguments
        self.message = message_fmt.format(
            artefact_type=artefact_type,
            activation_point=activation_point,
            termination_point=termination_point,
        )


class EXCEPTION_ARTEFACT_INVALID_POSITION(EXCEPTION_SNAKE_LADDER_SIMULATOR):
    message_fmt = "Invalid {artefact_type} ({activation_point}, {termination_point}): {artefact_type} extends outside the range of the board"

    def __init__(self, artefact_type, activation_point, termination_point):
        # TODO: Check if it is a good practice to instantiate custom exception with arguments
        super().__init__(
            self.message_fmt, artefact_type, activation_point, termination_point
        )


class EXCEPTION_ARTEFACT_LONG(EXCEPTION_SNAKE_LADDER_SIMULATOR):
    message_fmt = "Invalid {artefact_type} ({activation_point}, {termination_point}): spans the entire board"

    def __init__(self, artefact_type, activation_point, termination_point):
        # TODO: Check if it is a good practice to instantiate custom exception with arguments
        super().__init__(
            self.message_fmt, artefact_type, activation_point, termination_point
        )


class EXCEPTION_ARTEFACT_SHORT(EXCEPTION_SNAKE_LADDER_SIMULATOR):
    message_fmt = "Invalid {artefact_type} ({activation_point}, {termination_point}): Length of the {artefact_type} must span at least one row"

    def __init__(self, artefact_type, activation_point, termination_point):
        # TODO: Check if it is a good practice to instantiate custom exception with arguments
        super().__init__(
            self.message_fmt, artefact_type, activation_point, termination_point
        )


class EXCEPTION_ARTEFACT_INVERSE(EXCEPTION_SNAKE_LADDER_SIMULATOR):
    message_fmt = "Invalid {artefact_type} ({activation_point}, {termination_point}): {artefact_type} is inverse"

    def __init__(self, artefact_type, activation_point, termination_point):
        # TODO: Check if it is a good practice to instantiate custom exception with arguments
        super().__init__(
            self.message_fmt, artefact_type, activation_point, termination_point
        )


class EXCEPTION_SNAKE_AT_WINNING_POSITION(EXCEPTION_SNAKE_LADDER_SIMULATOR):
    message_fmt = "Invalid Snake ({activation_point}, {termination_point}): Snake is at winning position"

    def __init__(self, activation_point, termination_point):
        # TODO: Check if it is a good practice to instantiate custom exception with arguments
        super().__init__(self.message_fmt, "Snake", activation_point, termination_point)
