from argparse import ArgumentParser

from SBVR2ASP.asp.rule import Rule
from SBVR2ASP.data_structure.proposition import Proposition
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


def convert(proposition: Proposition, register: Register) -> Rule:
    res = Rule()
    for relation in proposition.relations:
        res.body.extend(relation.to_asp(register))
    return res


def main():
    arg_parser = ArgumentParser()
    arg_parser.add_argument("vocabulary", help="Vocabulary file")
    arg_parser.add_argument("rules", help="Rules file")
    args = arg_parser.parse_args()

    register = Register()

    # Process vocabulary
    with open(args.vocabulary, "r") as vocabulary_file:
        vocabulary = vocabulary_file.read()
    lark = LarkWrapper(Grammar.VOCABULARY)
    tree = lark.parse(vocabulary)
    VocabularyTransformer(register).transform(tree)

    # Process rules
    with open(args.rules, "r") as rules_file:
        rules = rules_file.read()
    rules = replace_concept_name(register.get_register(), rules)
    print(f'----\n{rules}\n----\n')

    lark = LarkWrapper(Grammar.RULES)
    tree = lark.parse(rules)
    concept_structure = RulesTransformer().transform(tree)

    res = []
    for proposition in concept_structure:
        res.append(convert(proposition, register))
    print("\n".join(map(str, res)))
