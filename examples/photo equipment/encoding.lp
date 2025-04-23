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
:- award(AWA), #count{photographer(PHOT): received_by(award(AWA),photographer(PHOT))} > 1.
:- jim(JIM), john(JOH), JIM = JOH.
:- g__gudas(GGUD), not gytis_gudas(GYTGUD), GGUD = GYTGUD.
:- person(PER), organization(ORG), PER = ORG.
:- commercial_organization(COMORG), other_organization(OTHORG), COMORG = OTHORG.
:- digital_photo_camera(DIGPHOCAM), #count{shooting_mode(SHOMOD): has(digital_photo_camera(DIGPHOCAM),shooting_mode(SHOMOD))} < 2.
:- photo_camera(PHOCAM), #count{memory_card_slot(MEMCARSLO): contains(photo_camera(PHOCAM),memory_card_slot(MEMCARSLO))} > 2.
:- photo_camera(PHOCAM), not 2 <= #count{white_balance_preset(WHIBALPRE): has(photo_camera(PHOCAM),white_balance_preset(WHIBALPRE))} <= 9.
:- digital_photo_camera(DIGPHOCAM), #count{photo_element(PHOELE): contains(digital_photo_camera(DIGPHOCAM),photo_element(PHOELE)), digital_photo_camera(DIGPHOCAM), photo_element(PHOELE), digital_sensor(DIGSEN), PHOELE = DIGSEN} < 1.
