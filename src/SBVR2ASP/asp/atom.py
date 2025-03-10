from __future__ import annotations

from SBVR2ASP.asp.i_operand import IOperand
from SBVR2ASP.asp.literal import Literal
from SBVR2ASP.asp.term import Term, ASP_NULL


class Atom(Literal, IOperand):
    def __init__(self, predicate: str, terms: dict[str, Term | Atom] = None, negated: bool = False):
        super().__init__()
        self.predicate = predicate
        if terms is None:
            terms = {'id': Term(ASP_NULL)}
        self.terms = terms
        self.negated = negated

    def init(self):
        if self.terms['id'] == ASP_NULL:
            self.terms['id'] = Term(''.join([x[0:3] for x in self.predicate.split('_')]).upper())

    def negate(self):
        self.negated = not self.negated

    def as_operand(self):
        return self.terms['id']

    def __str__(self):
        negation = 'not ' if self.negated else ''
        fields = []
        for value in self.terms.values():
            fields.append(str(value).replace('not ', ''))
        return f'{negation}{self.predicate}({",".join(fields)})'
