import enum

from SBVR2ASP.asp.literal import Literal


class MathOperator(enum.Enum):
    SUM = "+"
    DIFFERENCE = "-"
    PRODUCT = "*"
    DIVISION = "/"
    ABSOLUTE = "|"
    MODULO = "\\"
    GREATER_THAN = " > "
    GREATER_THAN_OR_EQUAL = " <= "
    LESS_THAN = " < "
    LESS_THAN_OR_EQUAL = " <= "
    EQUAL = " = "
    NOT_EQUAL = " != "


class Math(Literal):
    def __init__(self, operator: MathOperator, *operands: Literal):
        super().__init__()
        self.operator = operator
        self.operands = operands

    def negate(self):
        table = {MathOperator.GREATER_THAN: MathOperator.LESS_THAN_OR_EQUAL,
                 MathOperator.GREATER_THAN_OR_EQUAL: MathOperator.LESS_THAN,
                 MathOperator.LESS_THAN: MathOperator.GREATER_THAN_OR_EQUAL,
                 MathOperator.LESS_THAN_OR_EQUAL: MathOperator.GREATER_THAN,
                 MathOperator.EQUAL: MathOperator.NOT_EQUAL,
                 MathOperator.NOT_EQUAL: MathOperator.EQUAL}
        self.operator = table[self.operator]

    def __str__(self):
        if self.operator == MathOperator.ABSOLUTE:
            if len(self.operands) > 1:
                raise RuntimeError("Too many operands with absolute operator")
            return f"{self.operator.value}{self.operands[0]}{self.operator.value}"
        return f'{self.operator.value.join(map(str, self.operands))}'
