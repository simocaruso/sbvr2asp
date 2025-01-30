from SBVR2ASP.asp.literal import Literal
from SBVR2ASP.asp.term import Term, ASP_NULL


class Atom(Literal):
    def __init__(self, predicate: str, terms: dict[str, Term] = None, negation: bool = False):
        super().__init__()
        self.predicate = predicate
        if terms is None:
            terms = {'id': Term(ASP_NULL)}
        self.terms = terms
        self.negation = negation

    def __str__(self):
        negation = 'not ' if self.negation else ''
        return f'{negation}{self.predicate}({",".join(map(str, self.terms.values()))})'
