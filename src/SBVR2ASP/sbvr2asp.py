from argparse import ArgumentParser
from textwrap import indent

from SBVR2ASP.asp.rule import Rule
from SBVR2ASP.data_structure.relation import Node
from SBVR2ASP.debug import Debug
from SBVR2ASP.register import Register
from SBVR2ASP.transformers.rules import RulesTransformer
from SBVR2ASP.transformers.vocabulary import VocabularyTransformer
from SBVR2ASP.parser.lark_wrapper import LarkWrapper, Grammar


def replace_concept_name(register: dict, text: str) -> str:
    concept_names = list(register.keys())
    concept_names.sort(key=len, reverse=True)
    for concept_name in concept_names:
        text = text.replace(concept_name, register[concept_name])
    return text


def process_vocabulary(vocabulary: str, register: Register):
    lark = LarkWrapper(Grammar.VOCABULARY)
    tree = lark.parse(vocabulary)
    VocabularyTransformer(register).transform(tree)

def add_properties_to_grammar(lark: LarkWrapper, register: Register):
    added = {'is'}  # "is" should not be included and is handled in the grammar
    res = ''
    for property in register.get_properties().values():
        if property not in added:
            added.add(property)
            res += f'| \"{property} \"\n'
    res = res.removeprefix('| ')
    res = f'!verb: {indent(res, " " * len("!verb")).strip()}\n'
    lark.extend_grammar(res)

def process_rules(rules: str, register: Register) -> list[Node]:
    rules = replace_concept_name(register.get_register(), rules)
    lark = LarkWrapper(Grammar.RULES)
    '''
    !verb: "has "
    | "includes "
    | "establishes "
    | "owns "
    | "is owned by "
    | "incurs "
    | "is base for "
    | "is stored at "
    | "is provisionally charged to "
    | "is responsible for "
    | "is calculated in "
    | "honors "
    '''
    add_properties_to_grammar(lark, register)
    tree = lark.parse(rules)
    propositions = RulesTransformer(register).transform(tree)
    trees = []  # Contains one tree for each proposition
    queue = list(propositions)
    while queue:
        trees.append(queue[0].reshape([], queue))
        queue.pop(0)

    res: list[Rule] = []
    for tree in trees:
        curr = Rule()
        visited_nodes = set()
        for node in tree:
            node.evaluate(curr.body, register, visited_nodes, False)
        res.append(curr)
    return res


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("vocabulary", help="Vocabulary file")
    arg_parser.add_argument("rules", help="Rules file")
    args = arg_parser.parse_args()

    register = Register()
    Debug.register = register
    with open(args.vocabulary, 'r') as vocabulary:
        process_vocabulary(vocabulary.read(), register)

    with open(args.rules, 'r') as rules:
        res = process_rules(rules.read(), register)

    print("\n".join(map(str, res)))
