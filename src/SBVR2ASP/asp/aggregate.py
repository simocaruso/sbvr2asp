import enum

from SBVR2ASP.asp.literal import Literal
from SBVR2ASP.asp.math import MathOperator, Math
from SBVR2ASP.asp.term import Term


class AggregateOperator(enum.Enum):
    SUM = "sum"
    COUNT = "count"
    MIN = "min"
    MAX = "max"


class Aggregate(Literal):
    def __init__(self, aggregate_operator: AggregateOperator, aggregate_set_head=None, aggregate_set_body=None,
                 guard=None):
        super().__init__()
        if aggregate_set_head is None:
            aggregate_set_head = []
        if aggregate_set_body is None:
            aggregate_set_body = []
        self.aggregate_operator = aggregate_operator
        self.aggregate_set_head = aggregate_set_head
        self.aggregate_set_body = aggregate_set_body
        self.guard: tuple[Math, Math] = guard  # tuple lb, ub

    def negate(self):
        if self.guard[0]:
            self.guard[0].negate()
        if self.guard[1]:
            self.guard[1].negate()

    def __str__(self):
        res = (f'#{self.aggregate_operator.value}'
               f'{{{", ".join(map(str, self.aggregate_set_head))}: {", ".join(map(str, self.aggregate_set_body))}}}')
        if self.guard and self.guard[0]:
            res = str(Math(self.guard[0].operator, Term(res), *self.guard[0].operands))
        if self.guard and self.guard[1]:
            res = str(Math(self.guard[1].operator, Term(res), *self.guard[1].operands))
        return res
