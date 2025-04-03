from enum import Enum
from multiprocessing.resource_tracker import register
from typing import Any

import lark
from lark import Transformer, v_args

from SBVR2ASP.asp.math import MathOperator
from SBVR2ASP.data_structure.cardinality import ExactCardinality, Cardinality
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.data_structure.constant import Constant
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.data_structure.relation import Relation, MathRelation, SwappedLeftMostToRightMostRelation, \
    Disjunction, Conjunction, Implication, MatchRelation
from SBVR2ASP.data_structure.value import Value
from SBVR2ASP.register import Register

# Rule Type
NEGATIVE = 0,
POSITIVE = 1,
WEAK = 2


class TemporalValue(Enum):
    FUTURE = 0,
    PAST = 1


@v_args(inline=True)
class RulesTransformer(Transformer):
    def __init__(self, register: Register):
        super().__init__()
        self._register = register
        self._visited_concepts = set()

    def __default_token__(self, token):
        return token.value.strip()

    def start(self, *propositions) -> tuple[Node]:
        return propositions

    def proposition(self, proposition_expression) -> Node:
        self._visited_concepts.clear()
        return proposition_expression

    def positive_modal_operator(self):
        return POSITIVE

    def negative_modal_operator(self):
        return NEGATIVE

    def weak_modal_operator(self):
        return WEAK

    def universal_quantification(self):
        return None

    def existential_quantification(self):
        return Cardinality(1, None)

    def at_least_n_quantification(self, n):
        return Cardinality(n, None)

    def at_most_one_quantification(self):
        return Cardinality(None, 1)

    def at_most_n_quantification(self, n):
        return Cardinality(None, n)

    def exactly_one_quantification(self):
        return ExactCardinality(1)

    def exactly_n_quantification(self, n):
        return ExactCardinality(n)

    def numeric_range_quantification(self, lower_bound, upper_bound):
        return Cardinality(lower_bound, upper_bound)

    def at_least_n_quantification_with_n_2(self):
        return Cardinality(2, None)

    def logical_negation(self):
        return ExactCardinality(0)

    def modal_proposition(self, modal_operator, proposition_expression):
        if modal_operator == POSITIVE:
            proposition_expression.negated = not proposition_expression.negated
        elif modal_operator == WEAK:
            proposition_expression.weak = True
        return proposition_expression

    def modal_verb_proposition(self, p_exp_1, modal_verb, verb, p_exp_2):
        res = Relation(p_exp_1, p_exp_2)
        if modal_verb == POSITIVE:
            res.negated = not res.negated
        elif modal_verb == WEAK:
            res.weak = True
        return res

    def exclusive_disjunction(self, p_exp_1, p_exp_2):
        res = Conjunction(p_exp_1, p_exp_2)
        res.negated = not res.negated
        return res

    def equivalence(self, p_exp_1, p_exp_2):
        p_exp_2.negated = not p_exp_2.negated
        return Conjunction(p_exp_1, p_exp_2)

    def nand_formulation(self, p_exp_1, p_exp_2):
        res = Conjunction(p_exp_1, p_exp_2)
        res.negated = not res.negated
        return res

    def nor_formulation(self, p_exp_1, p_exp_2):
        return Disjunction(p_exp_1, p_exp_2)

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
        return MatchRelation(first, second)

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

    def temporal_proposition(self, first, second):
        operator = MathOperator.LESS_THAN
        if second == TemporalValue.FUTURE:
            operator = MathOperator.GREATER_THAN
        return MathRelation(first, Constant("now"), operator)

    def modal_verb(self, verb):
        modal = {
            "must": POSITIVE,
            "always": POSITIVE,
            "must not": NEGATIVE,
            "need not": NEGATIVE,
            "always": POSITIVE,
            "never": NEGATIVE,
            "can": WEAK,
            "may": WEAK
        }
        return modal[verb.strip().lower()]

    def temporal_value(self, value):
        if value == "in the future":
            return TemporalValue.FUTURE
        return TemporalValue.PAST

    def concept_proposition(self, concept):
        return concept

    def concept_of(self, first, second, conjunction):
        if conjunction:
            second = Disjunction(second, conjunction)
        return SwappedLeftMostToRightMostRelation(first, second)

    def concept_that(self, first, verb, second):
        return Relation(first, second)

    def concept_that_is(self, first, negation, second):
        if negation:
            second.negated = not second.negated
            return Relation(first, second)
        return Conjunction(first, MathRelation(first, second, MathOperator.EQUAL))

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
