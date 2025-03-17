from SBVR2ASP.asp.term import Term
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.register import Register


class Constant(Node):
    def __init__(self, value):
        super().__init__()
        self.value: str = value

    def reshape(self, tree: list[Node], queue):
        return tree

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        return Term(self.value), context

    def __repr__(self):
        return str(self.value)