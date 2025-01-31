from __future__ import annotations

import posix
from typing import TYPE_CHECKING

from SBVR2ASP.asp.aggregate import AggregateOperator, Aggregate
from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.asp.math import MathOperator, Math
from SBVR2ASP.asp.rule import Rule
from SBVR2ASP.asp.term import ASP_NULL, Term
from SBVR2ASP.register import Register

if TYPE_CHECKING:
    from SBVR2ASP.data_structure.concept import Concept
    from SBVR2ASP.data_structure.relation import Relation, OrderedRelation
    from SBVR2ASP.data_structure.proposition import Proposition


class Converter:

    def __init__(self, register: Register):
        self._encoding: list[Rule] = []
        self._current_rule = Rule()
        self._register = register

    def convert_propositions(self, propositions: list[Proposition]) -> list[Rule]:
        for proposition in propositions:
            proposition.convert(self)
        return self._encoding

    def convert_proposition(self, p: Proposition):
        for relation in p.relations:
            relation.convert(self)
            self._encoding.append(self._current_rule)
            self._current_rule = Rule()

    def link_atoms(self, relation: Atom, atom: Atom):
        if atom.terms['id'] == ASP_NULL:
            atom.terms['id'] = Term(''.join([x[0:3] for x in atom.predicate.split('_')]).upper())
        relation.terms[atom.predicate] = atom

    def convert_relation(self, r: Relation) -> Atom:
        first = r.left.convert(self)
        second = r.right.convert(self)
        relation_terms = {first.predicate: Term(ASP_NULL),
                          second.predicate: Term(ASP_NULL),
                          }
        relation = Atom(r.relation_name, relation_terms)
        self.link_atoms(relation, first)
        self.link_atoms(relation, second)
        res = [first]
        if r.right.cardinality is not None:
            aggregate = Aggregate(AggregateOperator.COUNT, [second], [relation], guard=r.right.cardinality.as_guard())
            if r.negated:
                aggregate.negate()
            res.append(aggregate)
        else:
            if r.negated:
                second.negate()
            res.append(second)
            res.append(relation)
        self._current_rule.body.extend(res)
        return second

    def convert_concept(self, c: Concept) -> Atom:
        return Atom(self._register.get_concept_name(c.concept_id))

    def convert_ordered_relation(self, r: OrderedRelation) -> Atom:
        first = r.left.convert(self)
        second = r.right.convert(self)
        self._current_rule.body.append(
            Math(MathOperator.GREATER_THAN, list(first.terms.values())[0], list(second.terms.values())[0]))
        return second
