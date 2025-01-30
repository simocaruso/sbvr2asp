import unittest

from SBVR2ASP.asp.math import MathOperator
from SBVR2ASP.data_structure.cardinality import Cardinality, ExactCardinality
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.data_structure.proposition import Proposition
from SBVR2ASP.parser.lark_wrapper import LarkWrapper, Grammar
from SBVR2ASP.register import Register
from SBVR2ASP.sbvr2asp import replace_concept_name
from SBVR2ASP.transformers.rules import RulesTransformer
from SBVR2ASP.transformers.vocabulary import VocabularyTransformer


class TestRules(unittest.TestCase):
    def test_rules(self):
        vocabulary = ('rental\n'
                      'requested car group\n'
                      'rental has requested car group\n')
        rules = 'It is necessary that each rental has exactly one requested car group.'
        register = Register()
        lark = LarkWrapper(Grammar.VOCABULARY)
        tree = lark.parse(vocabulary)
        VocabularyTransformer(register).transform(tree)
        rules = replace_concept_name(register.get_register(), rules)
        lark = LarkWrapper(Grammar.RULES)
        tree = lark.parse(rules)
        res: list[Proposition] = RulesTransformer().transform(tree)
        rental_id = register.get_concept_id('rental')
        car_group_id = register.get_concept_id('requested car group')
        self.assertIn(Concept(rental_id, None),
                      res[0].concepts)
        self.assertIn(Concept(car_group_id, ExactCardinality(1)), res[0].concepts)
