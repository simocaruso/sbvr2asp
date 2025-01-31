from argparse import ArgumentParser

from SBVR2ASP.asp.rule import Rule
from SBVR2ASP.data_structure.relation import Node
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


def process_rules(rules: str, register: Register) -> list[Node]:
    rules = replace_concept_name(register.get_register(), rules)
    lark = LarkWrapper(Grammar.RULES)
    tree = lark.parse(rules)
    propositions = RulesTransformer().transform(tree)

    reshaped_tree = []
    for proposition in propositions:
        reshaped_tree.append(proposition.reshape([]))

    res: list[Rule] = []
    for tree in reshaped_tree:
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
    with open(args.vocabulary, 'r') as vocabulary:
        process_vocabulary(vocabulary.read(), register)

    with open(args.rules, 'r') as rules:
        res = process_rules(rules.read(), register)

    print("\n".join(map(str, res)))
