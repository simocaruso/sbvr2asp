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
                        advance rental has scheduled pick-up date/time
                        ''')
        rules = dedent('''\
                    It is necessary that each rental has exactly one requested car group.
                    It is necessary that each rental includes exactly one rental period.
                    It is necessary that each rental has exactly one return branch.
                    It is necessary that the scheduled pick-up date/time of each advance rental is after the booking date/time of the rental booking that establishes the advance rental.''')
        register = Register()
        process_vocabulary(vocabulary, register)
        res = process_rules(rules, register)
        res = '\n'.join(map(str, res))
        self.assertEqual(res, dedent('''\
                                    :- rental(REN), #count{requested_car_group(REQCARGRO): has(rental(REN),requested_car_group(REQCARGRO))} != 1.
                                    :- rental(REN), #count{rental_period(RENPER): includes(rental(REN),rental_period(RENPER))} != 1.
                                    :- rental(REN), #count{return_branch(RETBRA): has(rental(REN),return_branch(RETBRA))} != 1.
                                    :- scheduled_pick_up_date_time(SCHPICUPDATTIM), booking_date_time(BOODATTIM), SCHPICUPDATTIM <= BOODATTIM, advance_rental(ADVREN), has(advance_rental(ADVREN),scheduled_pick_up_date_time(SCHPICUPDATTIM)), rental_booking(RENBOO), has(rental_booking(RENBOO),booking_date_time(BOODATTIM)), advance_rental(ADVREN), establishes(rental_booking(RENBOO),advance_rental(ADVREN)).'''))
