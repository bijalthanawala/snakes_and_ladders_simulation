class EXCEPTION_OBJECT_INVALID_POSITION(Exception):
    message = "Object extends outside the range of the board"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_OBJECT_LONG(Exception):
    message = "Object spans the entire board"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_OBJECT_SHORT(Exception):
    message = "Length of the object must span at least one row"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_OBJECT_INVERSE(Exception):
    message = "Object is inverse"

    def __init__(self):
        super().__init__(self.message)


class EXCEPTION_SNAKE_AT_WINNING_POSITION(Exception):
    message = "Snake is at winning position"

    def __init__(self):
        super().__init__(self.message)
