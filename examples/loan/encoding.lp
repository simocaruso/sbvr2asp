:- loan(LOA), #count{debtor(DEB): is_got_by(loan(LOA),debtor(DEB))} != 1.
:- loan(LOA), #count{bail(BAI): own(loan(LOA),bail(BAI))} != 1.
:- account(ACC), #count{bank(BAN): is_contained_in(account(ACC),bank(BAN))} != 1.
:- person(PER), #count{account(ACC): own(person(PER),account(ACC))} < 1.
:- person(PER), #count{account(ACC): own(person(PER),account(ACC))} > 5.
:- loan(LOA), #count{bank(BAN): is_given_by(loan(LOA),bank(BAN))} != 1.
:- real_estate(REAEST), #count{owner(OWN): is_owned_by(real_estate(REAEST),owner(OWN))} != 1.
