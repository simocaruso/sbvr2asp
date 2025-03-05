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
scheduled pick-up date/time
advance rental
booking date/time
rental booking
actual return date/time
rental organization unit

branch
Definition: rental organization unit

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

local area
rental car

return branch
Definition: branch

in-country rental
Definition: rental

car movement being round-trip
Definition: car movement

one-way car movement
Definition: car movement

one-way rental
Definition: rental

international rental
Definition: one-way rental

international inward rental
Definition: international rental

pick-up branch
Definition: branch

rented car
Definition: rental car

country
grace period
late return charge
country of registration
rented car
return branch has country
international inward rental has return branch
rental has rented car
rented car has country of registration
rental has actual return date/time
local area owns rental car
local area includes branch
branch is included in local area
rental is open
rented car is owned by local area
rental has pick-up branch
rental has grace period
grace period has end date/time
rental incurs late return charge

location penalty charge
EU-Rent site
drop-off location
rental has drop-off location
branch is located at EU-Rent site
rental incurs location penalty charge
EU-Rent site is base for rental organization unit

rental car is stored at branch

rental charge
estimated rental charge
Definition: rental charge
card

credit card
Definition: card
business currency
driver
rental has rental charge
rental charge is calculated in business currency

estimated rental charge is provisionally charged to card
renter has credit card
rental has driver
renter is responsible for rental
rental has business currency

cash rental
Definition: rental

cash rental price
Definition: base rental price

lowest rental price
Definition: cash rental price

cash rental honors lowest rental price
cash rental has base rental price
                        ''')
        rules = dedent('''\
// Rental Rules
It is necessary that each rental has exactly one requested car group.
It is necessary that each rental includes exactly one rental period.
It is necessary that each rental has exactly one return branch.
It is necessary that the scheduled pick-up date/time of each advance rental is after the booking date/time of the rental booking that establishes the advance rental.

// Charging / Billing / Payment Rules
It is permitted that a rental is open only if an estimated rental charge is provisionally charged to a credit card of the renter that is responsible for the rental.
It is necessary that the rental charge of each rental is calculated in the business currency of the rental.
It is necessary that each cash rental honors the lowest rental price of the cash rental.

// Pick-up / Return Rules
It is obligatory that the country of the return branch of each international inward rental is the country of registration of the rented car of the rental.
It is obligatory that at the actual return date/time of each in-country rental and each international inward rental the local area of the return branch of the rental owns the rented car of the rental.
It is obligatory that the country of the return branch of each international inward rental is the country of registration of the rented car of the rental.
It is necessary that if a rental is open and the rental is not an international inward rental then the rented car of the rental is owned by the local area of the pick-up branch of the rental.
If the actual return date/time of a rental is after the end date/time of the grace period of the rental then it is obligatory that the rental incurs a late return charge.
If the drop-off location of a rental is not the EU-Rent site that is base for the return branch of the rental then it is obligatory that the rental incurs a location penalty charge.
''')
        register = Register()
        process_vocabulary(vocabulary, register)
        res = process_rules(rules, register)
        res = '\n'.join(map(str, res))
        self.assertEqual(res, dedent('''\
:- rental(REN), #count{requested_car_group(REQCARGRO): has(rental(REN),requested_car_group(REQCARGRO))} != 1.
:- rental(REN), #count{rental_period(RENPER): includes(rental(REN),rental_period(RENPER))} != 1.
:- rental(REN), #count{return_branch(RETBRA): has(rental(REN),return_branch(RETBRA))} != 1.
:- scheduled_pick_up_date_time(SCHPICUPDATTIM), booking_date_time(BOODATTIM), SCHPICUPDATTIM <= BOODATTIM, advance_rental(ADVREN), has(advance_rental(ADVREN),scheduled_pick_up_date_time(SCHPICUPDATTIM)), rental_booking(RENBOO), has(rental_booking(RENBOO),booking_date_time(BOODATTIM)), advance_rental(ADVREN), establishes(rental_booking(RENBOO),advance_rental(ADVREN)).
:- rental(REN), open(OPE), REN = OPE, estimated_rental_charge(ESTRENCHA), not credit_card(CRECAR), is_provisionally_charged_to(estimated_rental_charge(ESTRENCHA),credit_card(CRECAR)), renter(REN), has(renter(REN),credit_card(CRECAR)), rental(REN), is_responsible_for(renter(REN),rental(REN)).
:- rental_charge(RENCHA), not business_currency(BUSCUR), is_calculated_in(rental_charge(RENCHA),business_currency(BUSCUR)), rental(REN), has(rental(REN),rental_charge(RENCHA)), rental(REN), has(rental(REN),business_currency(BUSCUR)).
:- cash_rental(CASREN), not lowest_rental_price(LOWRENPRI), honors(cash_rental(CASREN),lowest_rental_price(LOWRENPRI)), cash_rental(CASREN), honors(cash_rental(CASREN),lowest_rental_price(LOWRENPRI)).
:- country(COU), country_of_registration(COUOFREG), COU = COUOFREG, return_branch(RETBRA), has(return_branch(RETBRA),country(COU)), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),return_branch(RETBRA)), rented_car(RENCAR), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),rented_car(RENCAR)), has(rented_car(RENCAR),country_of_registration(COUOFREG)).
:- actual_return_date_time(ACTRETDATTIM), in_country_rental(INCOUREN), has(in_country_rental(INCOUREN),actual_return_date_time(ACTRETDATTIM)), local_area(LOCARE), rented_car(RENCAR), owns(local_area(LOCARE),rented_car(RENCAR)), return_branch(RETBRA), in_country_rental(INCOUREN), has(in_country_rental(INCOUREN),return_branch(RETBRA)), is_included_in(return_branch(RETBRA),local_area(LOCARE)), in_country_rental(INCOUREN), has(in_country_rental(INCOUREN),rented_car(RENCAR)).
:- country(COU), country_of_registration(COUOFREG), COU = COUOFREG, return_branch(RETBRA), has(return_branch(RETBRA),country(COU)), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),return_branch(RETBRA)), rented_car(RENCAR), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),rented_car(RENCAR)), has(rented_car(RENCAR),country_of_registration(COUOFREG)).
:- rental(REN), open(OPE), REN = OPE, rental(REN), not international_inward_rental(INTINWREN), REN = INTINWREN, rented_car(RENCAR), local_area(LOCARE), is_owned_by(rented_car(RENCAR),local_area(LOCARE)), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),rented_car(RENCAR)), pick_up_branch(PICUPBRA), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),pick_up_branch(PICUPBRA)), is_included_in(pick_up_branch(PICUPBRA),local_area(LOCARE)).
:- actual_return_date_time(ACTRETDATTIM), end_date_time(ENDDATTIM), ACTRETDATTIM > ENDDATTIM, rental(REN), has(rental(REN),actual_return_date_time(ACTRETDATTIM)), grace_period(GRAPER), rental(REN), has(rental(REN),grace_period(GRAPER)), has(grace_period(GRAPER),end_date_time(ENDDATTIM)), rental(REN), late_return_charge(LATRETCHA), incurs(rental(REN),late_return_charge(LATRETCHA)).
:- drop_off_location(DROOFFLOC), EU_Rent_site(EURENSIT), DROOFFLOC = EURENSIT, rental(REN), has(rental(REN),drop_off_location(DROOFFLOC)), not return_branch(RETBRA), not rental(REN), has(rental(REN),return_branch(RETBRA)), is_base_for(EU_Rent_site(EURENSIT),return_branch(RETBRA)), rental(REN), location_penalty_charge(LOCPENCHA), incurs(rental(REN),location_penalty_charge(LOCPENCHA)).
:- actual_return_date_time(ACTRETDATTIM), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),actual_return_date_time(ACTRETDATTIM)), local_area(LOCARE), rented_car(RENCAR), owns(local_area(LOCARE),rented_car(RENCAR)), return_branch(RETBRA), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),return_branch(RETBRA)), is_included_in(return_branch(RETBRA),local_area(LOCARE)), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),rented_car(RENCAR)).
''').strip())
