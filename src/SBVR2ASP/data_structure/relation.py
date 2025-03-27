import copy

from SBVR2ASP.asp.math import MathOperator, Math
from SBVR2ASP.data_structure.node import Node
from SBVR2ASP.register import Register


class Relation(Node):
    def __init__(self, left, right):
        super().__init__(left, right)

    def _reshaped_node(self):
        return Relation(self.left.get_left_most(),
                        self.right.get_left_most())

    def reshape(self, tree: list[Node], queue: list[Node]):
        res = self._reshaped_node()
        res.negated = self.negated
        res.weak = self.weak
        tree.append(res)
        tree = self.left.reshape(tree, queue)
        tree = self.right.reshape(tree, queue)
        return tree

    def _evaluate_left(self, context, register, visited):
        return self.left.evaluate(context, register, visited)

    def _evaluate_right(self, context, register, visited):
        return self.right.evaluate(context, register, visited, self.negated)

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        if self.id not in visited:
            visited.add(self.id)
        left, relation_context = self._evaluate_left(context, register, visited)
        right, relation_context = self._evaluate_right(context, register, visited)
        relation_atom = register.get_relation(self.left.concept_id, self.right.concept_id)
        if not relation_atom:
            relation_atom = register.get_relation(self.right.concept_id, self.left.concept_id)
        if not relation_atom:
            raise RuntimeError(
                f'No relation between {register.get_concept_name(self.left.concept_id)} and'
                f' {register.get_concept_name(self.right.concept_id)}')
        if relation_context == context:
            # Context changes only in case left or right are aggregates,
            # and in case they (or at least one) are aggregates the negation is already handled
            relation_atom.negated = self.negated
        register.link_atoms(relation_atom, left)
        register.link_atoms(relation_atom, right)
        if relation_atom:
            relation_context.append(relation_atom)
        return relation_atom, relation_context


class SwappedLeftMostToRightMostRelation(Relation):
    """
    Handle cases like the specification complement where:
        "a credit card of the renter"
    left and right children are swap and
    after the swap left most child is in relation with the right most.
    """

    def __init__(self, left, right):
        super().__init__(left, right)

    def _reshaped_node(self):
        res = Relation(self.right.get_left_most(),
                       self.left.get_right_most())
        res.negated = self.negated
        return res


class MathRelation(Relation):
    def __init__(self, left, right, operator: MathOperator):
        super().__init__(left, right)
        self.operator = operator

    def _reshaped_node(self):
        if self.negated and self.right.negated:
            # Remove double negation
            self.negated = False
            self.right.negated = False
        return MathRelation(self.left.get_left_most(),
                            self.right.get_left_most(),
                            self.operator)

    def get_left_most(self):
        return self

    def get_right_most(self):
        return self

    def evaluate(self, context: list, register: Register, visited: set, negated=False):
        if self.id not in visited:
            visited.add(self.id)
        left, new_context = self.left.get_left_most().evaluate(context, register, visited)
        right, new_context = self.right.get_left_most().evaluate(context, register, visited)
        left.init()
        right.init()
        res = Math(self.operator, left.as_operand(), right.as_operand())
        if self.negated:
            res.negate()
        if self.operator not in [MathOperator.SUM, MathOperator.PRODUCT, MathOperator.DIFFERENCE,
                                 MathOperator.DIVISION, MathOperator.ABSOLUTE, MathOperator.MODULO]:
            new_context.append(res)
        return res, new_context


class Disjunction(Node):
    """
    Disjunction is handled creating a new ASP rule and substituting the left child predicate with the right child predicate.
    """

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


class Conjunction(Node):
    """
    This node simply put together the children.
    """

    def __init__(self, left, right):
        super().__init__(left, right)

    def reshape(self, tree: list[Node], queue: list[Node]):
        tree = self.left.reshape(tree, queue)
        if self.negated:
            self.right.negated = not self.right.negated
        tree = self.right.reshape(tree, queue)
        return tree


class Implication(Conjunction):
    """
    This node handles logical implications.
    """

    def reshape(self, tree: list[Node], queue: list[Node]):
        return super().reshape(tree, queue)
