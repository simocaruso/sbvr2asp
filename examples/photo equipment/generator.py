import argparse
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


def generate(pool) -> list:
    res = []
    for _ in range(N):
        rating = pool.generate('rating')
        agent = pool.generate('agent')
        product = pool.generate('product')
        photo_camera = pool.generate('photo_camera')
        camera_model = pool.generate('camera_model')
        lens = pool.generate('lens')
        photo_element = pool.generate('photo_element')
        flash = pool.generate('flash')
        memory_card = pool.generate('memory_card')
        battery = pool.generate('battery')
        battery2 = pool.generate('battery')
        photo = pool.generate('photo')
        photographer = pool.generate('photographer')
        award = pool.generate('award')
        shooting_mode = pool.generate('shooting_mode')
        shooting_mode2 = pool.generate('shooting_mode')
        photo_exhibition = pool.generate('photo_exhibition')
        white_balance_preset = pool.generate('white_balance_preset')
        white_balance_preset2 = pool.generate('white_balance_preset')
        res.extend([rating, agent, photo_camera,
                    product, camera_model, lens,
                    award, photo_element, flash,
                    memory_card, battery])
        res.extend([Relation('is_given_by', rating, agent),
                    Relation('is_rating_of', rating, product),
                    Relation('contains', photo_camera, lens),
                    Relation('contains', photo_camera, photo_element),
                    Relation('contains', photo_camera, memory_card),
                    Relation('contains', photo_camera, flash),
                    Relation('contains', photo_camera, battery),
                    Relation('contains', photo_camera, battery2),
                    Relation('is_taken_by', photo, photo_camera),
                    Relation('received_in', award, photo_exhibition),
                    Relation('received_by', award, photographer),
                    Relation('received_for', award, photo),
                    Relation('has', photo_camera, camera_model),
                    Relation('has', photo_camera, shooting_mode),
                    Relation('contains', photo_camera, shooting_mode),
                    Relation('contains', photo_camera, shooting_mode2),
                    Relation('has', photo_camera, white_balance_preset),
                    Relation('has', photo_camera, white_balance_preset2),
                    ])
        if UNFEAS:
            res.append(Relation('is_given_by', rating,  pool.generate('agent')))
            res.append(Relation('is_rating_of', rating, pool.generate('product')))
            res.append(Relation('has', photo_camera, pool.generate('camera_model')))
            res.append(Relation('contains', photo_camera, pool.generate('lens')))
            res.append(Relation('contains', photo_camera, pool.generate('photo_element)')))
            res.append(Relation('contains', photo_camera, pool.generate('memory_card)')))
            res.append(Relation('contains', photo_camera, pool.generate('flash)')))
            res.append(Relation('contains', photo_camera, pool.generate('battery)')))
            res.append(Relation('received_in', award, pool.generate('photo_exhibition')))
            res.append(Relation('received_by', award, pool.generate('photographer')))
    return res


N = -1
UNFEAS = False

if __name__ == '__main__':
    pool = Pool()
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--number', default=100)
    args = parser.parse_args()
    N = int(args.number)
    print(' '.join(map(str, generate(pool))))
