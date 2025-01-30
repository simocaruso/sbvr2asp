import unittest

from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.asp.head_component import AssignmentHeadComponent, ChoiceHeadComponent
from SBVR2ASP.asp.rule import Rule
from SBVR2ASP.asp.term import Term


class TestAsp(unittest.TestCase):
    def test_asp(self):
        self.assertEqual(str(Rule(AssignmentHeadComponent([(Atom('atom', {'term': Term('1')}), [])]))),
                         'atom(1).')
        self.assertEqual(str(Rule(ChoiceHeadComponent([(Atom('atom', {'term': Term('1')}), [])]))),
                         '{atom(1)}.')
        self.assertEqual(str(Rule(ChoiceHeadComponent([(Atom('atom', {'term': Term('1')}), [])], cardinality=(1, 1)))),
                         '1 {atom(1)} 1.')
        self.assertEqual(str(Rule(None, [Atom('atom', {'term': Term('1')})])),
                         ':- atom(1).')
        self.assertEqual(str(Rule(None, [Atom('atom', {'term': Term('1')})], weight=Term('1'))),
                         ':~ atom(1). [1]')
