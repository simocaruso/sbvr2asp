from lark import Transformer, v_args

from SBVR2ASP.register import Register


class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_leaf = False


@v_args(inline=True)
class VocabularyTransformer(Transformer):
    def __init__(self, register: Register):
        super().__init__()
        self.register = register
        self.root = TrieNode()

    def start(self, *token):
        self.register.process_subclasses()

    def concept(self, concept, superclass):
        self.register.add_concept(concept)
        if superclass:
            self.register.add_subclass(concept, superclass)

    def concept_name(self, *first):
        res = ' '.join(first)
        self.register.add_concept(res)
        curr = self.root
        for token in first:
            if token not in curr.children:
                curr.children[token] = TrieNode()
            curr = curr.children[token]
        curr.is_leaf = True
        return res

    def property(self, *first):
        left_entity = ''
        property = ''
        curr = self.root
        i = 0
        while i < len(first):
            if first[i] in curr.children:
                curr = curr.children[first[i]]
                left_entity += first[i] + " "
                i += 1
            else:
                break
        if not curr.is_leaf:
            return self.concept_name(*first)
        while i < len(first) and not self.register.get_concept_id(' '.join(first[i:])):
            property += first[i] + " "
            i += 1
        if property and self.register.get_concept_id(' '.join(first[i:])):
            right_entity = ' '.join(first[i:])
            self.register.set_property(left_entity.strip(), right_entity.strip(), property.strip())
        else:
            return self.concept_name(*first)

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
