import copy

from SBVR2ASP.asp.math import MathOperator, Math
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.register import Register


class Relation(Node):
    def __init__(self, left, right, relation):
        super().__init__(left, right)
        self.relation_name = relation

    def reshape(self, tree: list[Node], queue: list[Node]):
        res = Relation(self.left.get_left_most(),
                       self.right.get_left_most(),
                       self.relation_name)
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree, queue)
        tree = self.right.reshape(tree, queue)
        return tree

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        if self.id not in visited:
            visited.add(self.id)
        left, relation_context = self.left.evaluate(context, register, visited)
        right, relation_context = self.right.evaluate(context, register, visited, self.negated)
        relation_atom = register.get_relation(self.left.concept_id, self.right.concept_id)
        register.link_atoms(relation_atom, left)
        register.link_atoms(relation_atom, right)
        if relation_atom:
            relation_context.append(relation_atom)


class ThatRelation(Relation):
    def __init__(self, left, right, relation):
        super().__init__(left, right, relation)

    def reshape(self, tree: list[Node], queue: list[Node]):
        res = Relation(self.get_right_most(self.left),
                       self.get_left_most(self.right),
                       self.relation_name)
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree, queue)
        tree = self.right.reshape(tree, queue)
        return [tree]

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        super().evaluate(context, register, visited)


class SpecificationComplementRelation(Node):
    def __init__(self, left, right):
        super().__init__(left, right)

    def reshape(self, tree: list[Node], queue: list[Node]):
        res = SpecificationComplementRelation(self.left.get_right_most(),
                                              self.right.get_left_most())
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree, queue)
        tree = self.right.reshape(tree, queue)
        return tree

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        if self.id not in visited:
            visited.add(self.id)
        left, new_context = self.left.evaluate(context, register, visited, self.negated)
        right, new_context = self.right.evaluate(context, register, visited, self.negated)
        relation_atom = register.get_relation(self.right.concept_id, self.left.concept_id)
        if not relation_atom:
            raise RuntimeError(
                f'No relation between {register.get_concept_name(self.right.concept_id)} and'
                f' {register.get_concept_name(self.left.concept_id)}')
        register.link_atoms(relation_atom, left)
        register.link_atoms(relation_atom, right)
        if relation_atom:
            new_context.append(relation_atom)


class MathRelation(Node):
    def __init__(self, left, right, operator: MathOperator):
        super().__init__(left, right)
        self.operator = operator

    def reshape(self, tree: list[Node], queue: list[Node]):
        res = MathRelation(self.left.get_left_most(),
                           self.right.get_left_most(),
                           self.operator)
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree, queue)
        tree = self.right.reshape(tree, queue)
        return tree

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        if self.id not in visited:
            visited.add(self.id)
        left, new_context = self.left.evaluate(context, register, visited)
        right, new_context = self.right.evaluate(context, register, visited)
        register.init(left)
        register.init(right)
        res = Math(self.operator, left.terms['id'], right.terms['id'])
        if self.negated:
            res.negate()
        new_context.append(res)
        return Math(self.operator, left, right)


class AtRelation(Node):
    def __init__(self, left, right):
        super().__init__(left, right)

    def reshape(self, tree: list[Node], queue: list[Node]):
        tree = self.left.reshape(tree, queue)
        tree = self.right.reshape(tree, queue)
        return tree


class SubstituteNode(Node):
    def __init__(self, left, right):
        super().__init__(left, right)
        self.left_processed = False
        self.right_processed = False

    def reshape(self, tree: list[Node], queue: list[Node]):
        if not self.left_processed:
            tree = self.left.reshape(tree, queue)
            self.left_processed = True
            new_proposition = copy.deepcopy(queue[0])
            new_proposition.replace_concept(self.left.concept_id, self.right.concept_id)
            queue.append(new_proposition)
        else:
            tree = self.right.reshape(tree, queue)
        return tree

    def get_left_most(self) -> Node:
        if not self.left_processed:
            return self.left.get_left_most()
        else:
            return self.right.get_left_most()

    def get_right_most(self) -> Node:
        if not self.left_processed:
            return self.left.get_right_most()
        else:
            return self.right.get_right_most()

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        raise RuntimeError("SubstituteNode should not be evaluated")
