from SBVR2ASP.asp.aggregate import Aggregate, AggregateOperator
from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.register import Register


class Concept:
    def __init__(self, concept_id, cardinality=None):
        self.concept_id = concept_id
        self.cardinality = cardinality

    def to_asp(self, register: Register):
        res = Atom(register.get_concept_name(self.concept_id))
        if self.cardinality is not None:
            return Aggregate(AggregateOperator.COUNT, [res], guard=self.cardinality.as_guard())
        return res

    def __eq__(self, other):
        if not isinstance(other, Concept):
            return False
        return self.concept_id == other.concept_id and self.cardinality == other.cardinality
