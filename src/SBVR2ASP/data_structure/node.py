from __future__ import annotations

from textwrap import indent

from SBVR2ASP.debug import Debug
from SBVR2ASP.register import Register


class Node:
    node_id = 0

    def __init__(self, left=None, right=None):
        self.left: Node = left
        self.right: Node = right
        self.negated = False
        self.substitute = {}
        self.id = Node.node_id
        Node.node_id += 1

    def get_left_most(self) -> Node:
        if not self.left:
            return self
        return self.left.get_left_most()

    def get_right_most(self) -> Node:
        if not self.right:
            return self
        return self.right.get_right_most()

    def reshape(self, tree: list[Node], queue: list[Node]) -> None:
        """Reshape the tree. New roots can be added to the tree
        :param tree:
        :param queue:
        """
        raise NotImplementedError()

    def replace_concept(self, to_substitute: str, new_value: str):
        if hasattr(self, 'concept_id') and self.concept_id == to_substitute:
            self.concept_id = new_value
        if self.left is not None:
            self.left.replace_concept(to_substitute, new_value)
        if self.right is not None:
            self.right.replace_concept(to_substitute, new_value)

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        """Evaluate the node making an ASP encoding"""
        raise NotImplementedError()

    def __repr__(self):
        try:
            return Debug.register.get_concept_name(self.left) + "-" + Debug.register.get_concept_name(self.right)
        except:
            return f'Left:\n{indent(self.left.__repr__(), "  ")}\n\nRight:\n{indent(self.right.__repr__(), "  ")}'
