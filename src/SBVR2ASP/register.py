import uuid
from collections import defaultdict

from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.asp.term import ASP_NULL, Term


class Register:
    def __init__(self):
        self._name_to_id = {}  # concept name, mapped id
        self._id_to_name = {}
        self._properties = {}

    def _generate_id(self) -> str:
        res = uuid.uuid4().hex
        while res in self._id_to_name:
            res = uuid.uuid4().hex
        return 'x' + res

    def get_register(self) -> dict:
        """
        Get the name to id dictionary.
        :return: the name to id dictionary
        """
        return self._name_to_id

    def get_concept_id(self, concept_name: str) -> str | None:
        concept_name = concept_name.replace('_', ' ')
        if concept_name not in self._name_to_id:
            return None
        return self._name_to_id[concept_name]

    def get_concept_name(self, concept_id: str) -> str | None:
        if concept_id not in self._id_to_name:
            return None
        return self._id_to_name[concept_id].replace(' ', '_')

    def get_relation(self, first_name: str, second_name: str) -> Atom | None:
        if not self.get_concept_id(first_name) or not self.get_concept_id(second_name):
            return None
        return self._create_atom(self._properties[(self.get_concept_id(first_name), self.get_concept_id(second_name))],
                                 [first_name, second_name])

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
            terms[name] = Term(ASP_NULL)
        return Atom(predicate.replace(' ', '_'), terms)
