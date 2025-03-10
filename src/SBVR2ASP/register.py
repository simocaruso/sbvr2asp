import copy
import uuid
from collections import defaultdict

from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.asp.term import ASP_NULL, Term


class Register:
    def __init__(self):
        self._name_to_id = {}  # concept name, mapped id
        self._id_to_name = {}
        self._properties = {}  # tuple of entities
        self._values = {}      # used to track values
        self._subclasses = defaultdict(list)  # list of subclasses of a concept

    def _generate_id(self) -> str:
        res = uuid.uuid4().hex
        while res in self._id_to_name:
            res = uuid.uuid4().hex
        return 'conceptidx' + res

    def get_register(self) -> dict:
        """
        Get the name to id dictionary.
        :return: the name to id dictionary
        """
        return self._name_to_id

    def get_properties(self):
        return self._properties

    def _clear_name(self, name: str) -> str:
        return name.replace(' ', '_').replace('/', '_').replace('-', '_')

    def get_concept_id(self, concept_name: str) -> str | None:
        if concept_name not in self._name_to_id:
            return None
        return self._name_to_id[concept_name]

    def get_concept_name(self, concept_id: str) -> str | None:
        if concept_id not in self._id_to_name:
            return None
        return self._clear_name(self._id_to_name[concept_id])

    def get_relation(self, first_id: str, second_id: str) -> Atom | None:
        if not (first_id, second_id) in self._properties:
            return None
        return self._create_atom(self._properties[first_id, second_id],
                                 [self._id_to_name[first_id], self._id_to_name[second_id]])

    def add_concept(self, concept_name: str):
        if concept_name not in self._name_to_id:
            id = self._generate_id()
            self._name_to_id[concept_name] = id
            self._id_to_name[id] = concept_name

    def set_property(self, first: str, second: str, property_name: str):
        if first not in self._name_to_id:
            self.add_concept(first)
        if second not in self._name_to_id:
            self.add_concept(second)
        self._properties[(self.get_concept_id(first), self.get_concept_id(second))] = property_name

    def get_atom(self, concept_id: str) -> Atom:
        if concept_id not in self._id_to_name:
            raise KeyError(f'Concept {concept_id} not registered')
        return self._create_atom(self._id_to_name[concept_id], ['id'])

    def _create_atom(self, predicate: str, term_names: list[str]) -> Atom:
        terms = {}
        for name in term_names:
            terms[self._clear_name(name)] = Term(ASP_NULL)
        return Atom(self._clear_name(predicate), terms)

    def link_atoms(self, relation: Atom, atom: Atom):
        atom.init()
        relation.terms[atom.predicate] = atom

    def add_subclass(self, concept: str, superclass: str):
        self._subclasses[self.get_concept_id(superclass)].append(self.get_concept_id(concept))

    def get_subclasses(self, concept: str) -> list[str]:
        return self._subclasses[concept]

    def add_value(self, value: str):
        self.add_concept(value)
        self._values[self.get_concept_id(value)] = value

    def process_subclasses(self):
        # Set all subclasses
        for id in self._id_to_name:
            curr = []
            queue = self._subclasses[id]
            while queue:
                curr.append(queue[0])
                queue.extend(self._subclasses[queue[0]])
                queue.pop(0)
            self._subclasses[id] = curr

        new_entries = {}
        for concepts, property_name in self._properties.items():
            for subclass in self._subclasses[concepts[0]]:
                new_entries[(subclass, concepts[1])] = property_name
            for subclass in self._subclasses[concepts[1]]:
                new_entries[(concepts[0], subclass)] = property_name
        self._properties.update(new_entries)

    def is_value(self, name):
        if name in self._values:
            return True
        return False