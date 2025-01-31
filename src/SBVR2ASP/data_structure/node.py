from __future__ import annotations

from SBVR2ASP.register import Register


class Node:
    node_id = 0

    def __init__(self, left=None, right=None):
        self.left = left
        self.right = right
        self.negated = False
        self.id = Node.node_id
        Node.node_id += 1

    def get_left_most(self, node: Node) -> Node:
        curr = node
        while curr.left:
            curr = curr.left
        return curr

    def get_right_most(self, node: Node) -> Node:
        curr = node
        while curr.right:
            curr = curr.right
        return curr

    def reshape(self, tree: list[Node]):
        """Reshape the tree. New roots can be added to the tree"""
        raise NotImplementedError()

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        """Evaluate the node making an ASP encoding"""
        raise NotImplementedError()
