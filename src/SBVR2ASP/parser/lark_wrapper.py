import enum
import os
from lark import Lark


class Grammar(enum.Enum):
    RULES = 'rules_grammar.lark'
    VOCABULARY = 'vocabulary_grammar.lark'


class LarkWrapper(object):
    def __init__(self, grammar: Grammar):
        with open(os.path.join(os.path.dirname(__file__), grammar.value)) as f:
            grammar = f.read()
        self.lark: Lark = Lark(grammar)

    def parse(self, text: str):
        text = text.strip() + '\n'
        return self.lark.parse(text)
