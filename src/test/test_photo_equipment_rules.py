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
digital sensor
photographic film
electronics product
creative product
other product
rating
agent
product
rating is given by agent
rating is rating of product

photo camera
digital photo camera
General Concept: photo camera
film photo camera
General Concept: photo camera

photo camera has camera model
lens
photo camera contains lens
photo element
photo camera contains photo element
photo camera contains flash
photo camera contains memory card
photo camera contains battery
photo is taken by photo camera
award received in photo exhibition
award received for photo
award received by photographer
Jim
John
person
organization
commercial organization
digital photo camera has shooting mode
photo camera contains memory card slot
photo camera has white balance preset
other organization
G. Gudas
Gytis Gudas''')


class TestPhotoEquipmentRules(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def _process(self, rules):
        register = Register()
        process_vocabulary(VOCABULARY, register)
        res = process_rules(rules, register)
        res = '\n'.join(map(str, res))
        return res

    def test_rules(self):
        rules = dedent('''\
                    It is impossible that digital sensor is photographic film.
                    It is impossible that electronics product is creative product.
                    It is impossible that electronics product is other product.
                    It is necessary that rating is given by exactly 1 agent.
                    It is necessary that rating is rating of exactly 1 product.
                    It is impossible that digital photo camera is film photo camera.
                    It is necessary that photo camera has at most 1 camera model.
                    It is necessary that photo camera contains exactly 1 lens.
                    It is necessary that photo camera contains exactly 1 photo element.
                    It is necessary that photo camera contains exactly 1 flash.
                    It is necessary that photo camera contains at most 2 memory card.
                    It is necessary that photo camera contains at least 1 memory card.
                    It is necessary that photo camera contains exactly 2 battery.
                    It is necessary that photo is taken by at most 1 photo camera.
                    It is impossible that digital photo camera is film photo camera.
                    It is necessary that award received in at most 1 photo exhibition.
                    It is necessary that award received for at least 1 photo.
                    It is necessary that award received by at most 1 photographer.
                    It is impossible that Jim is John.
                    It is necessary that G. Gudas is Gytis Gudas.
                    It is impossible that person is organization.
                    It is impossible that commercial organization is other organization.
                    It is necessary that photo camera contains at most 3 memory card.
                    It is necessary that photo camera contains at least 1 memory card.
                    It is necessary that digital photo camera has at least 2 shooting mode.
                    It is necessary that photo camera contains at most 2 memory card slot.
                    It is necessary that photo camera has at least 2 and at most 9 white balance preset.
                    It is necessary that digital photo camera contains photo element that is digital sensor.''')
        self.assertEqual(self._process(rules), dedent('''\
                            :- digital_sensor(DIGSEN), photographic_film(PHOFIL), DIGSEN = PHOFIL.
                            :- electronics_product(ELEPRO), creative_product(CREPRO), ELEPRO = CREPRO.
                            :- electronics_product(ELEPRO), other_product(OTHPRO), ELEPRO = OTHPRO.
                            :- rating(RAT), #count{agent(AGE): is_given_by(rating(RAT),agent(AGE))} != 1.
                            :- rating(RAT), #count{product(PRO): is_rating_of(rating(RAT),product(PRO))} != 1.
                            :- digital_photo_camera(DIGPHOCAM), film_photo_camera(FILPHOCAM), DIGPHOCAM = FILPHOCAM.
                            :- photo_camera(PHOCAM), #count{camera_model(CAMMOD): has(photo_camera(PHOCAM),camera_model(CAMMOD))} > 1.
                            :- photo_camera(PHOCAM), #count{lens(LEN): contains(photo_camera(PHOCAM),lens(LEN))} != 1.
                            :- photo_camera(PHOCAM), #count{photo_element(PHOELE): contains(photo_camera(PHOCAM),photo_element(PHOELE))} != 1.
                            :- photo_camera(PHOCAM), #count{flash(FLA): contains(photo_camera(PHOCAM),flash(FLA))} != 1.
                            :- photo_camera(PHOCAM), #count{memory_card(MEMCAR): contains(photo_camera(PHOCAM),memory_card(MEMCAR))} > 2.
                            :- photo_camera(PHOCAM), #count{memory_card(MEMCAR): contains(photo_camera(PHOCAM),memory_card(MEMCAR))} < 1.
                            :- photo_camera(PHOCAM), #count{battery(BAT): contains(photo_camera(PHOCAM),battery(BAT))} != 2.
                            :- photo(PHO), #count{photo_camera(PHOCAM): is_taken_by(photo(PHO),photo_camera(PHOCAM))} > 1.
                            :- digital_photo_camera(DIGPHOCAM), film_photo_camera(FILPHOCAM), DIGPHOCAM = FILPHOCAM.
                            :- award(AWA), #count{photo_exhibition(PHOEXH): received_in(award(AWA),photo_exhibition(PHOEXH))} > 1.
                            :- award(AWA), #count{photo(PHO): received_for(award(AWA),photo(PHO))} < 1.
                            :- award(AWA), #count{photographer(PHO): received_by(award(AWA),photographer(PHO))} > 1.
                            :- jim(JIM), john(JOH), JIM = JOH.
                            :- g__gudas(GGUD), not gytis_gudas(GYTGUD), GGUD = GYTGUD.
                            :- person(PER), organization(ORG), PER = ORG.
                            :- commercial_organization(COMORG), other_organization(OTHORG), COMORG = OTHORG.
                            :- photo_camera(PHOCAM), #count{memory_card(MEMCAR): contains(photo_camera(PHOCAM),memory_card(MEMCAR))} > 3.
                            :- photo_camera(PHOCAM), #count{memory_card(MEMCAR): contains(photo_camera(PHOCAM),memory_card(MEMCAR))} < 1.
                            :- digital_photo_camera(DIGPHOCAM), #count{shooting_mode(SHOMOD): has(digital_photo_camera(DIGPHOCAM),shooting_mode(SHOMOD))} < 2.
                            :- photo_camera(PHOCAM), #count{memory_card_slot(MEMCARSLO): contains(photo_camera(PHOCAM),memory_card_slot(MEMCARSLO))} > 2.
                            :- photo_camera(PHOCAM), not 2 <= #count{white_balance_preset(WHIBALPRE): has(photo_camera(PHOCAM),white_balance_preset(WHIBALPRE))} <= 9.
                            :- digital_photo_camera(DIGPHOCAM), #count{photo_element(PHOELE): contains(digital_photo_camera(DIGPHOCAM),photo_element(PHOELE)), digital_photo_camera(DIGPHOCAM), photo_element(PHOELE), digital_sensor(DIGSEN), PHOELE = DIGSEN} < 1.''').strip())
