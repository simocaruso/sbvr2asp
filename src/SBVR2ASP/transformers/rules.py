from multiprocessing.resource_tracker import register
from typing import Any

import lark
from lark import Transformer, v_args

from SBVR2ASP.asp.math import MathOperator
from SBVR2ASP.data_structure.cardinality import ExactCardinality, Cardinality
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.data_structure.relation import Relation, MathRelation, SwappedLeftMostToRightMostRelation, \
    Disjunction, Conjunction, Implication
from SBVR2ASP.data_structure.value import Value
from SBVR2ASP.register import Register

NEGATIVE = True
POSITIVE = False


@v_args(inline=True)
class RulesTransformer(Transformer):
    def __init__(self, register: Register):
        super().__init__()
        self._substitute = None
        self._register = register
        self._visited_concepts = set()

    def __default_token__(self, token):
        return token.value.strip()

    def start(self, *propositions) -> tuple[Node]:
        return propositions

    def proposition(self, proposition_expression) -> Node:
        self._visited_concepts.clear()
        proposition_expression.substitute = self._substitute
        return proposition_expression

    def necessity_formulation(self):
        return POSITIVE

    def obligation_formulation(self):
        return NEGATIVE

    def permissibility_formulation(self):
        return POSITIVE

    def universal_quantification(self):
        return None

    def exactly_one_quantification(self):
        return ExactCardinality(1)

    def at_least_n_quantification(self, n):
        return Cardinality(n, 0)

    def at_most_n_quantification(self, n):
        return Cardinality(0, n)

    def modal_proposition(self, modal_operator, proposition_expression):
        if modal_operator == POSITIVE:
            proposition_expression.negated = not proposition_expression.negated
        return proposition_expression

    def simple_proposition(self, subj, verb_negation, verb, obj):
        res = Relation(subj, obj)
        if verb_negation:
            res.negated = True
        return res

    def after_proposition(self, first, quantification, second):
        if quantification:
            return MathRelation(MathRelation(first, Value(quantification.concept_id, quantification.cardinality),
                                             MathOperator.SUM), second, MathOperator.GREATER_THAN)
        return MathRelation(first, second, MathOperator.GREATER_THAN)

    def before_proposition(self, first, quantification, second):
        if quantification:
            return MathRelation(MathRelation(first, Value(quantification.concept_id, quantification.cardinality),
                                             MathOperator.SUM), second, MathOperator.LESS_THAN)
        return MathRelation(first, second, MathOperator.LESS_THAN)

    def match_proposition(self, first, negation, second):
        if negation:
            second.negated = not second.negated
        return MathRelation(first, second, MathOperator.EQUAL)

    def implication_proposition(self, first, second):
        return Implication(first, second)

    def conditional_proposition(self, first, second):
        return Implication(first, second)

    def conjunction_proposition(self, first, second):
        return Conjunction(first, second)

    def disjunction_proposition(self, first, second):
        first.right = Disjunction(first.right, second)
        return first

    def at_proposition(self, first, second):
        return Conjunction(first, second)

    def concept_proposition(self, concept):
        return concept

    def concept_of(self, first, second, conjunction):
        if conjunction:
            second = Disjunction(second, conjunction)
        return SwappedLeftMostToRightMostRelation(first, second)

    def concept_that(self, first, verb, second):
        return Relation(first, second)

    def concept_with_property(self, first, second):
        property = self._register.get_relation(first.concept_id, second.concept_id)
        if property:
            return Relation(first, second)
        return Relation(second, first)

    def concept(self, quantification, name, label):
        if self._register.is_value(name):
            return Value(name, quantification)
        subclasses = self._register.get_subclasses(name)
        for subclass in subclasses:
            if subclass in self._visited_concepts:
                return Concept(subclass, quantification)
        self._visited_concepts.add(name)
        return Concept(name, quantification, label)

    def verb(self, token):
        return token

    def negation(self):
        return True

    def concept_name(self, token):
        return f'conceptid{token}'

    def NEWLINE(self, token):
        return lark.Discard
