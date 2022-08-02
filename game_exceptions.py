class EXCEPTION_ARTEFACT_INVALID_POSITION(Exception):
    message = "Artefact extends outside the range of the board"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_ARTEFACT_LONG(Exception):
    message = "Artefact spans the entire board"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_ARTEFACT_SHORT(Exception):
    message = "Length of the artefact must span at least one row"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_ARTEFACT_INVERSE(Exception):
    message = "Artefact is inverse"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_SNAKE_AT_WINNING_POSITION(Exception):
    message = "Snake is at winning position"

    def __init__(self):
        super().__init__(self.message)
