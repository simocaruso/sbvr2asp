from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.asp.term import ASP_NULL, Term
from SBVR2ASP.data_structure.concept import Concept
from SBVR2ASP.register import Register


class Relation:

    def __init__(self, relation, first, second):
        self.relation_name = relation
        self.first: Concept = first
        self.second: Concept = second

    def link_atoms(self, relation: Atom, atom: Atom):
        if atom.terms['id'] == ASP_NULL:
            atom.terms['id'] = Term(atom.predicate[0:3].upper())
        relation.terms[atom.predicate] = atom

    def to_asp(self, register: Register) -> list:
        res = [self.first.to_asp(register), self.second.to_asp(register)]
        relation_terms = {register.get_concept_name(self.first.concept_id): Term(ASP_NULL),
                          register.get_concept_name(self.second.concept_id): Term(ASP_NULL),
                          }
        relation = Atom(self.relation_name, relation_terms)
        self.link_atoms(relation, res[0])
        if self.second.cardinality is not None:
            res[1].aggregate_set_body.append(relation)
            self.link_atoms(relation, res[1].aggregate_set_head[0])
        else:
            self.link_atoms(relation, res[1])
        return res

