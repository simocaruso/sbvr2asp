import unittest
from textwrap import dedent

from SBVR2ASP.data_structure.cardinality import ExactCardinality
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.parser.lark_wrapper import LarkWrapper, Grammar
from SBVR2ASP.register import Register
from SBVR2ASP.sbvr2asp import replace_concept_name, process_vocabulary, process_rules
from SBVR2ASP.transformers.rules import RulesTransformer
from SBVR2ASP.transformers.vocabulary import VocabularyTransformer

VOCABULARY = dedent('''\
loan is got by debtor
loan own bail
account is contained in bank
person own account
loan is given by bank
real estate is owned by owner
''')


class TestLoanRules(unittest.TestCase):
    def _process(self, rules):
        register = Register()
        process_vocabulary(VOCABULARY, register)
        res = process_rules(rules, register)
        res = '\n'.join(map(str, res))
        return res

    def test_rules(self):
        rules = dedent('''\
                    It is necessary that loan is got by exactly 1 debtor.
                    It is necessary that loan own exactly 1 bail.
                    It is necessary that account is contained in exactly 1 bank.
                    It is necessary that person own at least 1 account.
                    It is necessary that person own at most 5 account.
                    It is necessary that loan is given by exactly 1 bank.
                    It is necessary that real estate is owned by exactly 1 owner.''')
        self.assertEqual(self._process(rules), dedent('''\
                            :- loan(LOA), #count{debtor(DEB): is_got_by(loan(LOA),debtor(DEB))} != 1.
                            :- loan(LOA), #count{bail(BAI): own(loan(LOA),bail(BAI))} != 1.
                            :- account(ACC), #count{bank(BAN): is_contained_in(account(ACC),bank(BAN))} != 1.
                            :- person(PER), #count{account(ACC): own(person(PER),account(ACC))} < 1.
                            :- person(PER), #count{account(ACC): own(person(PER),account(ACC))} > 5.
                            :- loan(LOA), #count{bank(BAN): is_given_by(loan(LOA),bank(BAN))} != 1.
                            :- real_estate(REAEST), #count{owner(OWN): is_owned_by(real_estate(REAEST),owner(OWN))} != 1.
                            ''').strip())
