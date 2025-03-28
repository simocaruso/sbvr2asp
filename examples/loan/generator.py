import random
from collections import defaultdict


class Atom:
    id = defaultdict(int)

    def __init__(self, predicate, id=None):
        self.predicate = predicate
        self.value = id
        if id is None:
            self.value = Atom.id[predicate]
            Atom.id[predicate] += 1

    def __str__(self):
        return f'{self.predicate}({self.value}).'


class Relation:
    def __init__(self, predicate, atom1, atom2):
        self.predicate = predicate
        self.atom1 = atom1
        self.atom2 = atom2

    def __str__(self):
        return f'{self.predicate}({str(self.atom1).removesuffix(".")},{str(self.atom2).removesuffix(".")}).'


class Pool:
    def __init__(self):
        self.pool = defaultdict(list)

    def generate(self, predicate):
        res = Atom(predicate)
        self.pool[predicate].append(res)
        return res

    def get(self, predicate, id):
        while Atom.id[predicate] < id:
            self.generate(predicate)
        return Atom(predicate, id)


def generate_banks(pool: Pool):
    res = []
    for _ in range(N_BANKS):
        res.append(pool.generate('bank'))
    return res


def generate(pool) -> list:
    res = []
    for _ in range(N_PERSONS):
        res.extend(generate_banks(pool))
        debtor = pool.generate('debtor')
        person = pool.generate('person')
        loan = pool.generate('loan')
        bail = pool.generate('bail')
        real_estate = pool.generate('real_estate')
        owner = pool.generate('owner')
        res.append(debtor)
        res.append(person)
        res.append(loan)
        res.append(bail)
        res.append(Relation('is_got_by', loan, debtor))
        bank_account = set()  # track the bank in which we create an account
        # create accounts
        for i in range(random.choice(N_ACCOUNT)):
            account = pool.generate('account')
            res.append(account)
            res.append(Relation('own', person, account))
            # select a random bank
            bank = pool.get('bank', random.randint(1, N_BANKS))
            bank_account.add(bank)
            res.append(Relation('is_contained_in', account, bank))
        res.append(Relation('is_given_by', loan, random.choice(list(bank_account))))
        res.append(Relation('own', loan, bail))
        res.append(Relation('is_owned_by', real_estate, owner))
    return res


# CONFIG
N_ACCOUNT = range(1, 6)  # range of number of accounts for each person
N_BANKS = 2  # total number of banks
N_PERSONS = 6  # total number of persons

if __name__ == '__main__':
    pool = Pool()
    print(' '.join(map(str, generate(pool))))
