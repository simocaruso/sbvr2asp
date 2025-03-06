from __future__ import annotations
from SBVR2ASP.asp.literal import Literal
from SBVR2ASP.asp.term import Term, ASP_NULL


class Atom(Literal):
    def __init__(self, predicate: str, terms: dict[str, Term | Atom] = None, negated: bool = False):
        super().__init__()
        self.predicate = predicate
        if terms is None:
            terms = {'id': Term(ASP_NULL)}
        self.terms = terms
        self.negated = negated

    def negate(self):
        self.negated = not self.negated

    def __str__(self):
        negation = 'not ' if self.negated else ''
        fields = []
        for value in self.terms.values():
            fields.append(str(value).replace('not ', ''))
        return f'{negation}{self.predicate}({",".join(fields)})'
