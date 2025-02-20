from SBVR2ASP.asp.math import MathOperator, Math
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.register import Register


class Relation(Node):
    def __init__(self, left, right, relation):
        super().__init__(left, right)
        self.relation_name = relation

    def reshape(self, tree: list[Node]):
        res = Relation(self.get_left_most(self.left),
                       self.get_left_most(self.right),
                       self.relation_name)
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree)
        tree = self.right.reshape(tree)
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

    def reshape(self, tree: list[Node]):
        res = Relation(self.get_right_most(self.left),
                       self.get_left_most(self.right),
                       self.relation_name)
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree)
        tree = self.right.reshape(tree)
        return tree

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        super().evaluate(context, register, visited)


class SpecificationComplementRelation(Node):
    def __init__(self, left, right):
        super().__init__(left, right)

    def reshape(self, tree: list[Node]):
        res = SpecificationComplementRelation(self.get_right_most(self.left),
                                              self.get_left_most(self.right))
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree)
        tree = self.right.reshape(tree)
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

    def reshape(self, tree: list[Node]):
        res = MathRelation(self.get_left_most(self.left),
                           self.get_left_most(self.right),
                           self.operator)
        res.negated = self.negated
        tree.append(res)
        tree = self.left.reshape(tree)
        tree = self.right.reshape(tree)
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
