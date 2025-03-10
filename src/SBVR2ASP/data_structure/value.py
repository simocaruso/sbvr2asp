from SBVR2ASP.asp.math import MathOperator
from SBVR2ASP.asp.term import Term
from SBVR2ASP.data_structure.cardinality import Cardinality
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.register import Register


class Value(Node):

    def __init__(self, concept_id, value):
        super().__init__()
        self.concept_id = concept_id
        self.value: Cardinality = value
        self.evaluate_res = None

    def reshape(self, tree: list[Node], queue):
        if self.value.upper_bound == self.value.lower_bound:
            tree[0].operator = MathOperator.LESS_THAN
        elif not self.value.upper_bound or not self.value.lower_bound:
            tree[0].operator = MathOperator.LESS_THAN
        return tree

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        value = self.value.upper_bound
        if not self.value.upper_bound:
            value = self.value.lower_bound
        return Term(self.value.upper_bound), context

    def __repr__(self):
        return str(self.value)
