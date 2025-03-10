from SBVR2ASP.asp.i_operand import IOperand
from SBVR2ASP.asp.literal import Literal

ASP_NULL = '_'


class Term(Literal, IOperand):
    def __init__(self, value: str = ASP_NULL):
        super().__init__()
        self.value = value

    def init(self):
        pass

    def as_operand(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, Term):
            return self.value == other.value
        if not isinstance(other, type(self.value)):
            return False
        return self.value == other

    def __str__(self):
        return self.value
