# Intend to replace the original Step
import re
from operator import itemgetter


GENERIC_MOVE_RE = re.compile(
    "([1-9][0-9]*|)([ULFRBD]w?|[MSEulfrbdxyz])(\'|i|2|2\'|)")
MOVE_RE = re.compile("()([ULFRBD]w?|[MSEulfrbdxyz])(\'|i|2|2\'|)")

CLOCKWISE = 1
HALFTURN = 2
COUNTER = 3


class GenericCubicMove(tuple):

    __slots__ = ()
    __regex__ = GENERIC_MOVE_RE

    def __new__(cls, representation):
        if isinstance(representation, GenericCubicMove):
            symbol = representation.symbol
            sign = representation.sign
            level = representation.level

        elif isinstance(representation, tuple) and len(representation) == 3:
            level, symbol, sign = representation
            assert isinstance(level, int) and level > 0 and \
                symbol in "ULFRBDMSEulfrbdxyz" and sign in (1, 2, 3), \
                "Invalid Move initialisation: {}".format(representation)

        elif isinstance(representation, str):
            match = cls.__regex__.match(representation.strip())
            if match is None:
                raise ValueError("Invalid move: {}".format(representation))
            level, symbol, sign = match.groups()
            if "w" in symbol:
                symbol = symbol[0].lower()
            if level == "":
                if symbol in "ulfrbd":
                    level = "2"
                else:
                    level = "1"
            level = int(level)
            if sign == "2'":
                sign = "2"
            if sign == "i":
                sign = "'"
            sign = [None, "", "2", "'"].index(sign)

        else:
            raise ValueError("Can only accept Move, str, or 3-element tuple")

        if symbol in "ulfrbd" and level == 1:
            symbol = symbol.upper()
        if symbol in "MSExyz":
            level = 1

        return super().__new__(cls, (level, symbol, sign))

    level = property(itemgetter(0))
    symbol = property(itemgetter(1))
    sign = property(itemgetter(2))

    def __repr__(self):
        level = self.level
        if level == 1 or (self.symbol in "ulfrbd" and level == 2):
            level = ""
        return str(level) + self.symbol + [None, "", "2", "'"][self.sign]

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, move):
        if not isinstance(move, self.__class__):
            move = self.__class__(move)
        return super().__eq__(move)

    def __ne__(self, move):
        return not self.__eq__(move)

    def __add__(self, move):
        if not isinstance(move, self.__class__):
            move = self.__class__(move)
        assert self.symbol == move.symbol and self.level == move.level, \
            "Can't operate addition on two Moves with different symbols"
        sign = (self.sign + move.sign) % 4
        if sign == 0:
            return 0
        return self.__class__((self.level, self.symbol, sign))

    def __mul__(self, i):
        assert isinstance(i, int), "Can only multiply with an integer"
        sign = (self.sign * i) % 4
        if sign == 0:
            return 0
        return self.__class__((self.level, self.symbol, sign))

    def inverse(self):
        return self.__class__((self.level, self.symbol, 4 - self.sign))


if __name__ == "__main__":
    Move = GenericCubicMove
    m = Move("R")
    assert m * 3 == m.inverse() == Move("R'")
    assert m + Move("R'") == 0
    assert m + Move("R") == Move("R2")
    assert Move("l'") == Move("li") == Move((2, "l", 3)) == Move(Move("l'"))
    assert {Move("M'"): 4}["M'"] == 4
