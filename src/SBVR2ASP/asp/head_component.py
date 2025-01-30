from SBVR2ASP.asp.atom import Atom
from SBVR2ASP.asp.literal import Literal


class HeadComponent(object):
    def __init__(self, head: list[(Atom, list[Literal])]):
        self.head = head

    def join_head(self, separator: str) -> str:
        res = ''
        for atom, literals in self.head:
            res += f'{atom}'
            if literals:
                res += f': {literals}'
            res += f'{separator}'
        return res.removesuffix(separator).strip()

    def __str__(self):
        return ''

    def __repr__(self):
        return self.__str__()


class ChoiceHeadComponent(HeadComponent):
    def __init__(self, head: list[(Atom, list[Literal])], cardinality: (int, int) = (None, None)):
        super().__init__(head)
        self.cardinality = self.parse_cardinality(cardinality)

    def parse_cardinality(self, cardinality):
        res = ['', '']
        res[0] = cardinality[0] if cardinality[0] is not None else ''
        res[1] = cardinality[1] if cardinality[1] is not None else ''
        return res

    def __str__(self):
        return f'{self.cardinality[0]} {{{self.join_head(";")}}} {self.cardinality[1]}'


class AssignmentHeadComponent(HeadComponent):
    def __init__(self, head: list[(Atom, list[Literal])]):
        super().__init__(head)

    def __str__(self):
        return self.join_head('|')
