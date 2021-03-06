import os
import argparse
import json

from pygments import highlight
from pygments.lexers.javascript import JavascriptLexer
from pygments.formatters.terminal import TerminalFormatter
from tinydb import TinyDB, Query


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--data_source', type=str, required=True)
    p_args = parser.parse_args()

    db = TinyDB(os.path.abspath(p_args.data_source))

    eq_table = db.table('equivalence')
    mt_table = db.table('mutants')

    mutants = []

    for mutant in mt_table.all():
        if len(eq_table.search(
            (Query().name == mutant['name']) &
            (Query().compile_error == False)
        )) > 0:
            mutants.append(mutant['name'])

    valid_configurations = eq_table.search(Query().invalid_configuration == False)
    configurations = []
    operators = {}

    for configuration in valid_configurations:
        if configuration['name'] in mutants and not configuration['compile_error']:
            configurations.append(configuration)

    for conf in configurations:

        if conf['operator'] not in operators.keys():
            operators[conf['operator']] = {
                'operator': conf['operator'],
                'mutants_total': len(mt_table.search(Query().operator == conf['operator'])),
                'mutants': [],
                'mutants_equivalent': [],
                'mutants_not_equivalent': []
            }

        if conf['name'] not in operators[conf['operator']]['mutants']:
            operators[conf['operator']]['mutants'].append(conf['name'])

        if conf['useless']:
            if conf['name'] not in operators[conf['operator']]['mutants_equivalent']:
                operators[conf['operator']]['mutants_equivalent'].append(conf['name'])
        else:
            if conf['name'] not in operators[conf['operator']]['mutants_not_equivalent']:
                operators[conf['operator']]['mutants_not_equivalent'].append(conf['name'])

    partially_equivalent = 0
    totally_equivalent = 0
    totally_not_equivalent = 0

    for op_name in operators.keys():
        mutants_partially_equivalent = []
        mutants_totally_equivalent = []
        mutants_totally_not_equivalent = []

        op = operators[op_name]
        for mutant in op['mutants']:
            if mutant in op['mutants_not_equivalent'] and mutant in op['mutants_equivalent']:
                mutants_partially_equivalent.append(mutant)
            elif mutant in op['mutants_not_equivalent'] and mutant not in op['mutants_equivalent']:
                mutants_totally_not_equivalent.append(mutant)
            elif mutant not in op['mutants_not_equivalent'] and mutant in op['mutants_equivalent']:
                mutants_totally_equivalent.append(mutant)

        op['mutants_partially_equivalent'] = len(mutants_partially_equivalent)
        op['mutants_totally_not_equivalent'] = len(mutants_totally_not_equivalent)
        op['mutants_totally_equivalent'] = len(mutants_totally_equivalent)

        partially_equivalent += len(mutants_partially_equivalent)
        totally_equivalent += len(mutants_totally_equivalent)
        totally_not_equivalent += len(mutants_totally_not_equivalent)

        print(str(op['operator']) + ',' + str(op['mutants_total']) + ','
              + str(len(mutants_partially_equivalent)) + ', ,' +
              str(len(mutants_totally_equivalent)) + ', ,' +
              str(len(mutants_totally_not_equivalent)) + ', ,')

    print(highlight(
        code=json.dumps(operators, indent=2, sort_keys=True),
        lexer=JavascriptLexer(),
        formatter=TerminalFormatter()
    ))

    macros = len(db.search(Query().type == 'config')[0]['macros'])

    print(str(macros) + ',' + str(len(mt_table.all())) + ',' + str(partially_equivalent)
          + ', ,' + str(totally_equivalent) + ', ,' + str(totally_not_equivalent)
          + ', ,')

    print(len(eq_table.all()))
    print(len(eq_table.search((Query().compile_error == False))))
    print(len(eq_table.search((Query().compile_error == True))))

    mutants_with_compilation_error = []
    mutants_without_compilation_error = []
    mutants_without_compilation_error_2 = []
    mutants_without_compilation_error_3 = []

    for mutant in mt_table.all():
        if len(eq_table.search(
            (Query().name == mutant['name']) &
            (Query().compile_error == True) &
            (Query().invalid_configuration == False)
        )) > 0:
            mutants_with_compilation_error.append(mutant['name'])

        if len(eq_table.search(
                (Query().name == mutant['name']) &
                (Query().compile_error == True) &
                (Query().invalid_configuration == False)
        )) == 0:
            mutants_without_compilation_error.append(mutant['name'])

        if len(eq_table.search(
                (Query().name == mutant['name']) &
                (Query().compile_error == True) &
                (Query().invalid_configuration == True)
        )) > 0:
            mutants_without_compilation_error_2.append(mutant['name'])

            if len(eq_table.search(
                    (Query().name == mutant['name']) &
                    (Query().compile_error == False) &
                    (Query().invalid_configuration == True)
            )) > 0:
                mutants_without_compilation_error_2.append(mutant['name'])

    print("------------------")
    print(len(mutants_with_compilation_error))
    print(len(mutants_without_compilation_error))
    print(len(mutants_without_compilation_error_2))
    print(len(mutants_without_compilation_error_3))
    print(len(mt_table.all()))

