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
rental
requested car group
period
rental period
General Concept: period

period overlap period

scheduled pick-up date/time
advance rental
booking date/time
rental booking
actual return date/time
rental organization unit

branch
General Concept: rental organization unit

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
General Concept: branch

in-country rental
General Concept: rental

car movement being round-trip
General Concept: car movement

one-way car movement
General Concept: car movement

one-way rental
General Concept: rental

international rental
General Concept: one-way rental

international inward rental
General Concept: international rental

pick-up branch
General Concept: branch

rented car
General Concept: rental car

country
grace period
late return charge
country of registration
General Concept: country
rented car
branch has country
international inward rental has return branch
rental has rented car
rental car has country of registration
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
General Concept: rental charge
card

credit card
General Concept: card
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
General Concept: rental

cash rental price
General Concept: base rental price

lowest rental price
General Concept: cash rental price

cash rental honors lowest rental price
cash rental has base rental price

driver
primary driver
General Concept: driver
rental has primary driver
driver is barred
driver is qualified

rental has renter

need of service
scheduled service
rental car is in need of service
rental car is in need of repair
rental car has scheduled service
rental incurs car exchange during rental

car transfer
transfer drop-off branch
General Concept: branch
transfer drop-off date/time
transferred car
General Concept: rental car
rental car is owned by local area
local area includes branch
international return
General Concept: car transfer
car transfer has transfer drop-off branch
car transfer has transfer drop-off date/time
car transfer has transferred car

points rental
General Concept: rental

rental is assigned

club member
General Concept: renter
start date/time
actual start date/time
General Concept: start date/time
rental has start date/time
rental car has fuel level

full
Concept type: individual concept
miles
Concept type: individual concept
rental car has service reading
rental has rental duration
service reading
rental duration
rental days
Concept type: individual concept
days
scheduled start date/time
rental has scheduled start date/time
rental has booking date/time
renter requests price conversion
price conversion has currency
rental charge is converted to currency

rental has pick-up branch
rental car is stored at branch
rental has start date
reserved rental
General Concept: rental
''')


class TestCarRentalRules(unittest.TestCase):
    def _process(self, rules):
        self.maxDiff = None
        register = Register()
        process_vocabulary(VOCABULARY, register)
        res = process_rules(rules, register)
        res = '\n'.join(map(str, res))
        return res

    def test_rental_rules(self):
        rules = dedent('''\
                    // Rental Rules
                    It is necessary that each rental has exactly one requested car group.
                    It is necessary that each rental includes exactly one rental period.
                    It is necessary that each rental has exactly one return branch.
                    It is necessary that the scheduled pick-up date/time of each advance rental is after the booking date/time of the rental booking that establishes the advance rental.
                    ''')
        self.assertEqual(self._process(rules), dedent('''\
                            :- rental(REN), #count{requested_car_group(REQCARGRO): has(rental(REN),requested_car_group(REQCARGRO))} != 1.
                            :- rental(REN), #count{rental_period(RENPER): includes(rental(REN),rental_period(RENPER))} != 1.
                            :- rental(REN), #count{return_branch(RETBRA): has(rental(REN),return_branch(RETBRA))} != 1.
                            :- scheduled_pick_up_date_time(SCHPICUPDATTIM), booking_date_time(BOODATTIM), SCHPICUPDATTIM <= BOODATTIM, advance_rental(ADVREN), has(advance_rental(ADVREN),scheduled_pick_up_date_time(SCHPICUPDATTIM)), rental_booking(RENBOO), has(rental_booking(RENBOO),booking_date_time(BOODATTIM)), advance_rental(ADVREN), establishes(rental_booking(RENBOO),advance_rental(ADVREN)).
                            ''').strip())

    def test_payment_rules(self):
        rules = dedent('''\
                    // Charging / Billing / Payment Rules
                    It is permitted that a rental is open only if an estimated rental charge is provisionally charged to a credit card of the renter that is responsible for the rental.
                    It is necessary that the rental charge of each rental is calculated in the business currency of the rental.
                    If the renter of a rental requests a price conversion then it is obligatory that the rental charge of the rental is converted to the currency of the price conversion.
                    It is necessary that each cash rental honors the lowest rental price of the cash rental.''')
        self.assertEqual(self._process(rules), dedent('''\
                                :- rental(REN), open(OPE), REN = OPE, #count{credit_card(CRECAR): is_provisionally_charged_to(estimated_rental_charge(ESTRENCHA),credit_card(CRECAR)), estimated_rental_charge(ESTRENCHA), credit_card(CRECAR), renter(RENT), has(renter(RENT),credit_card(CRECAR)), rental(REN), is_responsible_for(renter(RENT),rental(REN))} < 1.
                                :- rental_charge(RENCHA), #count{business_currency(BUSCUR): is_calculated_in(rental_charge(RENCHA),business_currency(BUSCUR)), rental_charge(RENCHA), business_currency(BUSCUR), rental(REN), has(rental(REN),business_currency(BUSCUR))} < 1, rental(REN), has(rental(REN),rental_charge(RENCHA)).
                                :- renter(RENT), price_conversion(PRICON), requests(renter(RENT),price_conversion(PRICON)), rental(REN), has(rental(REN),renter(RENT)), #count{currency(CUR): is_converted_to(rental_charge(RENCHA),currency(CUR)), rental_charge(RENCHA), currency(CUR), price_conversion(PRICON), has(price_conversion(PRICON),currency(CUR))} < 1, rental(REN), has(rental(REN),rental_charge(RENCHA)).
                                :- cash_rental(CASREN), #count{lowest_rental_price(LOWRENPRI): honors(cash_rental(CASREN),lowest_rental_price(LOWRENPRI)), cash_rental(CASREN), lowest_rental_price(LOWRENPRI), cash_rental(CASREN), honors(cash_rental(CASREN),lowest_rental_price(LOWRENPRI))} < 1.''').strip())

    def test_driver_rules(self):
        rules = dedent('''\
        // Driver rules
        It is permitted that a rental is open only if each driver of the rental is not a barred driver.
        It is obligatory that each driver of a rental is qualified.''')
        self.assertEqual(self._process(rules), dedent('''\
                                :- rental(REN), open(OPE), REN = OPE, driver(DRI), driver(DRI), DRI = DRI, rental(REN), has(rental(REN),driver(DRI)), barred(BAR), is(driver(DRI),barred(BAR)).
                                :- driver(DRI), not qualified(QUA), DRI = QUA, rental(REN), has(rental(REN),driver(DRI)).
                                ''').strip())

    def test_return_rules(self):
        rules = dedent('''\
                    // Pick-up / Return Rules
                    It is obligatory that the country of the return branch of each international inward rental is the country of registration of the rented car of the rental.
                    It is obligatory that at the actual return date/time of each in-country rental and each international inward rental the local area of the return branch of the rental owns the rented car of the rental.
                    It is obligatory that the country of the return branch of each international inward rental is the country of registration of the rented car of the rental.
                    It is necessary that if a rental is open and the rental is not an international inward rental then the rented car of the rental is owned by the local area of the pick-up branch of the rental.
                    If the actual return date/time of a rental is after the end date/time of the grace period of the rental then it is obligatory that the rental incurs a late return charge.
                    If a rental is assigned then it is obligatory that the rented car of the rental is stored at the pick-up branch of the rental.
                    If the drop-off location of a rental is not the EU-Rent site that is base for the return branch of the rental then it is obligatory that the rental incurs a location penalty charge.
                    ''')
        self.assertEqual(self._process(rules), dedent('''\
                                        :- country(COU), country_of_registration(COUOFREG), COU != COUOFREG, return_branch(RETBRA), has(return_branch(RETBRA),country(COU)), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),return_branch(RETBRA)), international_inward_rental(INTINWREN), rented_car(RENCAR), has(international_inward_rental(INTINWREN),rented_car(RENCAR)), has(rented_car(RENCAR),country_of_registration(COUOFREG)).
                                        :- in_country_rental(INCOUREN), actual_return_date_time(ACTRETDATTIM), has(in_country_rental(INCOUREN),actual_return_date_time(ACTRETDATTIM)), #count{rented_car(RENCAR): owns(local_area(LOCARE),rented_car(RENCAR)), local_area(LOCARE), rented_car(RENCAR), in_country_rental(INCOUREN), has(in_country_rental(INCOUREN),rented_car(RENCAR))} < 1, in_country_rental(INCOUREN), return_branch(RETBRA), has(in_country_rental(INCOUREN),return_branch(RETBRA)), is_included_in(return_branch(RETBRA),local_area(LOCARE)).
                                        :- country(COU), country_of_registration(COUOFREG), COU != COUOFREG, return_branch(RETBRA), has(return_branch(RETBRA),country(COU)), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),return_branch(RETBRA)), international_inward_rental(INTINWREN), rented_car(RENCAR), has(international_inward_rental(INTINWREN),rented_car(RENCAR)), has(rented_car(RENCAR),country_of_registration(COUOFREG)).
                                        :- rental(REN), open(OPE), REN = OPE, rental(REN), not international_inward_rental(INTINWREN), REN = INTINWREN, #count{local_area(LOCARE): is_owned_by(rented_car(RENCAR),local_area(LOCARE)), rented_car(RENCAR), local_area(LOCARE), international_inward_rental(INTINWREN), pick_up_branch(PICUPBRA), has(international_inward_rental(INTINWREN),pick_up_branch(PICUPBRA)), is_included_in(pick_up_branch(PICUPBRA),local_area(LOCARE))} < 1, international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),rented_car(RENCAR)).
                                        :- actual_return_date_time(ACTRETDATTIM), end_date_time(ENDDATTIM), ACTRETDATTIM > ENDDATTIM, rental(REN), has(rental(REN),actual_return_date_time(ACTRETDATTIM)), rental(REN), grace_period(GRAPER), has(rental(REN),grace_period(GRAPER)), has(grace_period(GRAPER),end_date_time(ENDDATTIM)), #count{late_return_charge(LATRETCHA): incurs(rental(REN),late_return_charge(LATRETCHA)), rental(REN), late_return_charge(LATRETCHA)} < 1.
                                        :- rental(REN), assigned(ASS), REN = ASS, #count{pick_up_branch(PICUPBRA): is_stored_at(rented_car(RENCAR),pick_up_branch(PICUPBRA)), rented_car(RENCAR), pick_up_branch(PICUPBRA), rental(REN), has(rental(REN),pick_up_branch(PICUPBRA))} < 1, rental(REN), has(rental(REN),rented_car(RENCAR)).
                                        :- drop_off_location(DROOFFLOC), eu_rent_site(EURENSIT), DROOFFLOC != EURENSIT, rental(REN), has(rental(REN),drop_off_location(DROOFFLOC)), rental(REN), return_branch(RETBRA), has(rental(REN),return_branch(RETBRA)), is_base_for(eu_rent_site(EURENSIT),return_branch(RETBRA)), #count{location_penalty_charge(LOCPENCHA): incurs(rental(REN),location_penalty_charge(LOCPENCHA)), rental(REN), location_penalty_charge(LOCPENCHA)} < 1.
                                        :- international_inward_rental(INTINWREN), actual_return_date_time(ACTRETDATTIM), has(international_inward_rental(INTINWREN),actual_return_date_time(ACTRETDATTIM)), #count{rented_car(RENCAR): owns(local_area(LOCARE),rented_car(RENCAR)), local_area(LOCARE), rented_car(RENCAR), international_inward_rental(INTINWREN), has(international_inward_rental(INTINWREN),rented_car(RENCAR))} < 1, international_inward_rental(INTINWREN), return_branch(RETBRA), has(international_inward_rental(INTINWREN),return_branch(RETBRA)), is_included_in(return_branch(RETBRA),local_area(LOCARE)).
                                        ''').strip())

    def test_rental_period(self):
        rules = dedent('''\
                        // Rental Period Rules
                        It is obligatory that the start date of each reserved rental is in the future.
                        It is obligatory that the rental duration of each rental is at most 90 rental days.
                        If rental1 is not rental2 and the renter of rental1 is the renter of rental2 then it is obligatory that the rental period of rental1 does not overlap the rental period of rental2.
                        ''')
        self.assertEqual(self._process(rules), dedent('''\
                                    :- start_date(STADAT), STADAT <= now, reserved_rental(RESREN), has(reserved_rental(RESREN),start_date(STADAT)).
                                    :- rental_duration(RENDUR), RENDUR >= 90, rental(REN), has(rental(REN),rental_duration(RENDUR)).
                                    :- rental(REN_1), rental(REN_2), REN_1 != REN_2, renter(RENT_1), renter(RENT_2), RENT_1 = RENT_2, rental(REN_1), has(rental(REN_1),renter(RENT_1)), rental(REN_2), has(rental(REN_2),renter(RENT_2)), rental_period(RENPER_1), rental_period(RENPER_2), overlap(rental_period(RENPER_1),rental_period(RENPER_2)), rental(REN_1), includes(rental(REN_1),rental_period(RENPER_1)), rental(REN_2), includes(rental(REN_2),rental_period(RENPER_2)).
                                    ''').strip())

    def test_servicing_rules(self):
        rules = dedent('''\
                // Servicing Rules
                It is obligatory that each rental car in need of service has a scheduled service.
                It is obligatory that the service reading of a rental car is at most 5500 miles.
                If the rented car of an open rental is in need of service or is in need of repair then it is obligatory that the rental incurs a car exchange during rental.
                ''')
        self.assertEqual(self._process(rules), dedent('''\
                            :- rental_car(RENTCAR), #count{scheduled_service(SCHSER): has(rental_car(RENTCAR),scheduled_service(SCHSER)), rental_car(RENTCAR), scheduled_service(SCHSER)} < 1, in_need_of_service(INNEEOFSER), is(rental_car(RENTCAR),in_need_of_service(INNEEOFSER)).
                            :- service_reading(SERREA), SERREA >= 5500, rental_car(RENTCAR), has(rental_car(RENTCAR),service_reading(SERREA)).
                            :- rented_car(RENCAR), in_need_of_service(INNEEOFSER), RENCAR = INNEEOFSER, rental(REN), has(rental(REN),rented_car(RENCAR)), open(OPE), is(rental(REN),open(OPE)), #count{car_exchange_during_rental(CAREXCDURREN): incurs(rental(REN),car_exchange_during_rental(CAREXCDURREN)), rental(REN), car_exchange_during_rental(CAREXCDURREN)} < 1.
                            :- rented_car(RENCAR), in_need_of_repair(INNEEOFREP), RENCAR = INNEEOFREP, rental(REN), has(rental(REN),rented_car(RENCAR)), open(OPE), is(rental(REN),open(OPE)), #count{car_exchange_during_rental(CAREXCDURREN): incurs(rental(REN),car_exchange_during_rental(CAREXCDURREN)), rental(REN), car_exchange_during_rental(CAREXCDURREN)} < 1.
                            ''').strip())

    def test_points_rental_rules(self):
        rules = dedent('''
                    // Points Rental Rules
                    It is necessary that the renter of each points rental is a club member.
                    It is necessary that the booking date/time of a points rental is at least 5 days before the scheduled start date/time of the rental.
                    ''')
        self.assertEqual(self._process(rules), dedent('''\
                            :- renter(RENT), not club_member(CLUMEM), RENT = CLUMEM, points_rental(POIREN), has(points_rental(POIREN),renter(RENT)).
                            :- booking_date_time(BOODATTIM), scheduled_start_date_time(SCHSTADATTIM), BOODATTIM+5 >= SCHSTADATTIM, points_rental(POIREN), has(points_rental(POIREN),booking_date_time(BOODATTIM)), points_rental(POIREN), has(points_rental(POIREN),scheduled_start_date_time(SCHSTADATTIM)).
                            ''').strip())

    def test_transfer_rules(self):
        rules = dedent('''
                // Transfer Rules
                At the transfer drop-off date/time of a car transfer it is obligatory that the transferred car of the car transfer is owned by the local area that includes the transfer drop-off branch of the car transfer.
                It is obligatory that the country of the transfer drop-off branch of an international return is the country of registration of the transferred car of the international return.
                At the transfer drop-off date/time of an international return it is obligatory that the transferred car of the international return is owned by the local area that includes the transfer drop-off branch of the international return.''')
        self.assertEqual(self._process(rules), dedent('''\
                                    :- car_transfer(CARTRA), transfer_drop_off_date_time(TRADROOFFDATTIM), has(car_transfer(CARTRA),transfer_drop_off_date_time(TRADROOFFDATTIM)), #count{local_area(LOCARE): is_owned_by(transferred_car(TRACAR),local_area(LOCARE)), transferred_car(TRACAR), local_area(LOCARE), car_transfer(CARTRA), transfer_drop_off_branch(TRADROOFFBRA), has(car_transfer(CARTRA),transfer_drop_off_branch(TRADROOFFBRA)), includes(local_area(LOCARE),transfer_drop_off_branch(TRADROOFFBRA))} < 1, car_transfer(CARTRA), has(car_transfer(CARTRA),transferred_car(TRACAR)).
                                    :- country(COU), country_of_registration(COUOFREG), COU != COUOFREG, transfer_drop_off_branch(TRADROOFFBRA), has(transfer_drop_off_branch(TRADROOFFBRA),country(COU)), international_return(INTRET), has(international_return(INTRET),transfer_drop_off_branch(TRADROOFFBRA)), international_return(INTRET), transferred_car(TRACAR), has(international_return(INTRET),transferred_car(TRACAR)), has(transferred_car(TRACAR),country_of_registration(COUOFREG)).
                                    :- international_return(INTRET), transfer_drop_off_date_time(TRADROOFFDATTIM), has(international_return(INTRET),transfer_drop_off_date_time(TRADROOFFDATTIM)), #count{local_area(LOCARE): is_owned_by(transferred_car(TRACAR),local_area(LOCARE)), transferred_car(TRACAR), local_area(LOCARE), international_return(INTRET), transfer_drop_off_branch(TRADROOFFBRA), has(international_return(INTRET),transfer_drop_off_branch(TRADROOFFBRA)), includes(local_area(LOCARE),transfer_drop_off_branch(TRADROOFFBRA))} < 1, international_return(INTRET), has(international_return(INTRET),transferred_car(TRACAR)).                                    ''').strip())
