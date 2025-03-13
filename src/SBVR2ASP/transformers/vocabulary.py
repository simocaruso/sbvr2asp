from lark import Transformer, v_args

from SBVR2ASP.register import Register


@v_args(inline=True)
class VocabularyTransformer(Transformer):
    def __init__(self, register: Register):
        super().__init__()
        self.register = register

    def start(self, *token):
        self.register.process_subclasses()

    def concept(self, concept, superclass):
        self.register.add_concept(concept)
        if superclass:
            self.register.add_subclass(concept, superclass)

    def property(self, first, property_name, second):
        self.register.set_property(first, second, property_name.strip())

    def definition(self, name):
        return name

    def value(self, value):
        self.register.add_value(value)

    def spaced_name(self, first, second):
        return f"{first} {second}"

    def dot_name(self, first, second):
        return f"{first}. {second}"

    def dashed_name(self, first, second):
        return f"{first}-{second}"

    def slashed_name(self, first, second):
        return f"{first}/{second}"

    def WORD(self, word):
        return word.value
