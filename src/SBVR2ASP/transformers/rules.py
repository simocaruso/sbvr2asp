import lark
from lark import Transformer, v_args

from SBVR2ASP.data_structure.cardinality import ExactCardinality, Cardinality
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.data_structure.proposition import Proposition
from SBVR2ASP.data_structure.relation import Relation

NEGATIVE = True
POSITIVE = False


@v_args(inline=True)
class RulesTransformer(Transformer):
    def __init__(self):
        super().__init__()
        self._propositions: list[Proposition] = []
        self._current_proposition = Proposition()

    def __default_token__(self, token):
        return token.value.strip()

    def start(self) -> list[Proposition]:
        return self._propositions

    def proposition(self):
        self._propositions.append(self._current_proposition)
        self._current_proposition = Proposition()
        return lark.Discard

    def necessity_formulation(self):
        return POSITIVE

    def universal_quantification(self):
        return None

    def exactly_one_quantification(self):
        return ExactCardinality(1)

    def modal_proposition(self, modal_operator, proposition_expression):
        if modal_operator == POSITIVE:
            proposition_expression.negated = True
        return lark.Discard

    def simple_proposition(self, subj, verb, obj):
        res = Relation(verb, subj, obj)
        self._current_proposition.relations.append(res)
        return res

    def concept(self, quantification, name):
        res = Concept(name, quantification)
        self._current_proposition.concepts.append(res)
        return res

    def verb(self, token):
        return token

    def NEWLINE(self, token):
        return lark.Discard
