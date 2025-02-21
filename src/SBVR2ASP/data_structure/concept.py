from SBVR2ASP.asp.aggregate import AggregateOperator, Aggregate
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.debug import Debug
from SBVR2ASP.register import Register


class Concept(Node):
    def __init__(self, concept_id, cardinality=None):
        super().__init__()
        self.concept_id = concept_id
        self.cardinality = cardinality
        self.evaluate_res = None

    def reshape(self, tree: list[Node], queue):
        return tree

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        if self.id not in visited:
            visited.add(self.id)
            atom = register.get_atom(self.concept_id)
            new_context = context
            if self.cardinality:
                aggregate = Aggregate(AggregateOperator.COUNT, [atom], [],
                                      guard=self.cardinality.as_guard())
                if negated:
                    aggregate.negate()
                new_context = aggregate.aggregate_set_body
                context.append(aggregate)
            else:
                if negated:
                    atom.negate()
                context.append(atom)
            self.evaluate_res = atom, new_context
        return self.evaluate_res

    def __eq__(self, other):
        if not isinstance(other, Concept):
            return False
        return self.concept_id == other.concept_id and self.cardinality == other.cardinality

    def __repr__(self):
        return Debug.register.get_concept_name(self.concept_id)
