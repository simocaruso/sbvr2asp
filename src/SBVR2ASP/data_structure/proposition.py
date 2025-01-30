from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.data_structure.relation import Relation


class Proposition:
    def __init__(self):
        self.relations: list[Relation] = []
        self.concepts: list[Concept] = []
        self.negated = False
