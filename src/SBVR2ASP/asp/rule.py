from SBVR2ASP.asp.head_component import HeadComponent
from SBVR2ASP.asp.literal import Literal


class Rule:
    def __init__(self, head: HeadComponent = None, body: list[Literal] = None, /, level: list[Literal] = None,
                 weight: Literal | None = None):
        if head is None:
            head = HeadComponent([])
        self.head = head
        if body is None:
            body = []
        self.body = body
        if level is None:
            level = []
        self.level = level
        self.weight = weight
        self.relations = []

    def __str__(self):
        res = f'{self.head}'
        separator = ':-'
        if self.level or self.weight:
            separator = ':~'
        if self.body:
            res += f' {separator} {", ".join(map(str, self.body))}'
        res = res.strip() + '.'
        if self.weight:
            res += f' [{self.weight}'
            if self.level:
                res += f'@{", ".join(map(str, self.level))}'
            res += ']'
        return res

    def __repr__(self):
        return self.__str__()
