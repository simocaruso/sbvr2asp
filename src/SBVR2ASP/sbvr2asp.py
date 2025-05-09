import uuid
from argparse import ArgumentParser
from textwrap import indent

from SBVR2ASP.asp.rule import Rule
from SBVR2ASP.data_structure.relation import Node
from SBVR2ASP.debug import Debug
from SBVR2ASP.register import Register
from SBVR2ASP.transformers.rules import RulesTransformer
from SBVR2ASP.transformers.vocabulary import VocabularyTransformer
from SBVR2ASP.parser.lark_wrapper import LarkWrapper, Grammar


def replace_concept_name(name_to_id: dict, properties: list[str], text: str) -> str:
    properties = set(properties)
    concept_names = list(name_to_id.keys()) + list(properties)
    concept_names.sort(key=len, reverse=True)
    tmp = {}
    for concept_name in concept_names:
        if concept_name in properties:
            tmp[concept_name] = uuid.uuid4().hex
            text = text.replace(concept_name, tmp[concept_name])
        else:
            text = text.replace(concept_name, name_to_id[concept_name] + '#')
    for id, value in tmp.items():
        text = text.replace(value, id)
    return text


def process_vocabulary(vocabulary: str, register: Register):
    lark = LarkWrapper(Grammar.VOCABULARY)
    tree = lark.parse(vocabulary)
    VocabularyTransformer(register).transform(tree)


def add_properties_to_grammar(lark: LarkWrapper, register: Register):
    added = {'is', 'be'}  # "is" should not be included and is handled in the grammar
    res = ''
    for property in register.get_properties().values():
        if property not in added:
            added.add(property)
            res += f'| \"{property} \"\n'
    res = res.removeprefix('| ')
    res = f'!verb: {indent(res, " " * len("!verb")).strip()}\n'
    lark.extend_grammar(res)


def process_rules(rules: str, register: Register) -> list[Node]:
    rules = replace_concept_name(register.get_register(), register.get_properties().values(), rules)
    lark = LarkWrapper(Grammar.RULES)
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
            if node.weak:
                curr.weight = 1
        res.append(curr)
    return res


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("vocabulary", help="Vocabulary file")
    arg_parser.add_argument("rules", help="Rules file")
    arg_parser.add_argument("--ngo", action='store_true')
    args = arg_parser.parse_args()

    register = Register()
    Debug.register = register
    with open(args.vocabulary, 'r') as vocabulary:
        process_vocabulary(vocabulary.read(), register)

    with open(args.rules, 'r') as rules:
        res = process_rules(rules.read(), register)

    encoding = "\n".join(map(str, res))

    if args.ngo:
        from clingo.ast import parse_string
        from ngo import optimize, auto_detect_input, auto_detect_output
        prg = []
        parse_string(encoding, prg.append)
        encoding = '\n'.join(map(str, optimize(prg, auto_detect_input(prg), auto_detect_output(prg))))

    print(encoding)
