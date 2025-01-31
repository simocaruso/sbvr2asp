import unittest
from textwrap import dedent

from SBVR2ASP.data_structure.cardinality import ExactCardinality
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.parser.lark_wrapper import LarkWrapper, Grammar
from SBVR2ASP.register import Register
from SBVR2ASP.sbvr2asp import replace_concept_name, process_vocabulary, process_rules
from SBVR2ASP.transformers.rules import RulesTransformer
from SBVR2ASP.transformers.vocabulary import VocabularyTransformer


class TestRules(unittest.TestCase):
    def test_rules(self):
        vocabulary = dedent('''\
                        rental
                        requested car group
                        rental period
                        return branch
                        scheduled pick-up date/time
                        advance rental
                        booking date/time
                        rental booking
                        
                        rental booking has booking date/time
                        rental booking establishes advance rental
                        rental includes rental period
                        rental has requested car group
                        rental has return branch
                        rental has scheduled pick-up date/time
                        
                        
                        advance rental includes rental period
                        advance rental has requested car group
                        advance rental has return branch
                        advance rental has scheduled pick-up date/time''')
        rules = 'It is necessary that each rental has exactly one requested car group.'
        register = Register()
        process_vocabulary(vocabulary, register)
        res = process_rules(rules, register)
        self.assertEqual(str(res[0]),
                         ':- not rental(REN), #count{requested_car_group(REQCARGRO): has(not rental(REN),requested_car_group(REQCARGRO))} != 1.')
