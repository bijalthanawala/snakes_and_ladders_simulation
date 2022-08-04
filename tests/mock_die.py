class Mock_Die:
    def __init__(self, rolls):
        self.rolls = rolls
        self.ndx = 0

    def roll(self):
        n = self.rolls[self.ndx]
        self.ndx = (self.ndx + 1) % len(self.rolls)
        return n
