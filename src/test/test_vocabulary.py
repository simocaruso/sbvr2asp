import unittest

from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.asp.term import ASP_NULL, Term
from SBVR2ASP.parser.lark_wrapper import LarkWrapper, Grammar
from SBVR2ASP.register import Register
from SBVR2ASP.transformers.vocabulary import VocabularyTransformer


class TestVocabulary(unittest.TestCase):
    def test_vocabulary(self):
        text = ('car movement\n'
                'car movement has receiving branch')
        tree = LarkWrapper(Grammar.VOCABULARY).parse(text)
        register = Register()
        VocabularyTransformer(register).transform(tree)
        self.assertTrue(register.get_concept_id('car movement'))
        self.assertTrue(register.get_concept_id('receiving branch'))
        self.assertEqual(str(register.get_relation(register.get_concept_id('car movement'),
                                                   register.get_concept_id('receiving branch'))), 'has(_,_)', )
        self.assertEqual(str(register.get_atom(register.get_concept_id('car movement'))), 'car_movement(_)')
