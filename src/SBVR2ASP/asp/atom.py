from __future__ import annotations

from collections import defaultdict

from SBVR2ASP.asp.i_operand import IOperand
from SBVR2ASP.asp.literal import Literal
from SBVR2ASP.asp.term import Term, ASP_NULL


class Atom(Literal, IOperand):
    logic_vars = {}

    def __init__(self, predicate: str, terms: dict[str, Term | Atom] = None, negated: bool = False, label: str = False):
        super().__init__()
        self.predicate = predicate
        self.label = label
        if terms is None:
            terms = {'id': Term(ASP_NULL)}
        self.terms = terms
        self.negated = negated

    def init(self):
        if self.terms['id'] == ASP_NULL:
            last = 3
            res = ''.join([x[0:last] for x in self.predicate.split('_')]).upper()
            while res in Atom.logic_vars and Atom.logic_vars[res] != self.predicate:
                last += 1
                res = ''.join([x[0:last] for x in self.predicate.split('_')]).upper()
            Atom.logic_vars[res] = self.predicate
            if self.label:
                res += '_' + self.label
            self.terms['id'] = Term(res)

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
