from typing import Any

import lark
from lark import Transformer, v_args

from SBVR2ASP.asp.math import MathOperator
from SBVR2ASP.data_structure.cardinality import ExactCardinality
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.data_structure.relation import Relation, MathRelation, SpecificationComplementRelation

NEGATIVE = True
POSITIVE = False


@v_args(inline=True)
class RulesTransformer(Transformer):
    def __init__(self):
        super().__init__()

    def __default_token__(self, token):
        return token.value.strip()

    def start(self, *propositions) -> tuple[Node]:
        return propositions

    def proposition(self, proposition_expression) -> Node:
        return proposition_expression

    def necessity_formulation(self):
        return POSITIVE

    def obligation_formulation(self):
        return NEGATIVE

    def universal_quantification(self):
        return None

    def exactly_one_quantification(self):
        return ExactCardinality(1)

    def modal_proposition(self, modal_operator, proposition_expression):
        if modal_operator == POSITIVE:
            proposition_expression.negated = True
        return proposition_expression

    def simple_proposition(self, subj, verb, obj):
        return Relation(subj, obj, verb)

    def after_proposition(self, first, second):
        return MathRelation(first, second, MathOperator.GREATER_THAN)

    def match_proposition(self, first, second):
        return MathRelation(first, second, MathOperator.EQUAL)

    def concept_proposition(self, concept):
        return concept

    def concept_of_each(self, first, second):
        return SpecificationComplementRelation(first, second)

    def concept_that(self, first, verb, second):
        return Relation(first, second, verb)

    def concept(self, quantification, name):
        return Concept(name, quantification)

    def verb(self, token):
        return token

    def NEWLINE(self, token):
        return lark.Discard
