import os
import shutil
import argparse
import json

from pygments import highlight
from pygments.lexers.javascript import JavascriptLexer
from pygments.formatters.terminal import TerminalFormatter

from spl_mutants.db.state import Config
from spl_mutants.db.product_state import ProductState
from spl_mutants.impact_analysis_runner import ImpactAnalysisRunner
from spl_mutants.products.product_generator import ProductGenerator
from spl_mutants.products.gcc_strategies import gcc_to_tce
from spl_mutants.checker.equivalence import EquivalenceChecker
from spl_mutants.checker.duplicate import DuplicateChecker


def main():
    config = Config()

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source_file', type=str, required=True)
    parser.add_argument('-M', '--mutants_dir', type=str, required=True)
    parser.add_argument('-O', '--output_dir', type=str, required=True)
    parser.add_argument('-P', '--gcc_params', type=str, required=False)
    parser.add_argument('-I', '--includes', nargs='*', required=False)
    parser.add_argument('-D', '--defines', nargs='*', required=False)
    parser.add_argument('-U', '--undefines', nargs='*', required=False)
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument('-E', '--debug', default=False, action='store_true')
    parser.add_argument('--disable-impact-analysis', default=False, action='store_true')
    parser.add_argument('--no-check-duplicates', default=False, action='store_true')

    p_args = parser.parse_args()

    config.output_dir = os.path.abspath(p_args.output_dir)
    config.mutants_dir = os.path.abspath(p_args.mutants_dir)
    config.source_file = os.path.abspath(p_args.source_file)
    gcc_params = ['-D' + a for a in p_args.defines] if p_args.defines is not None else []
    gcc_params += ['-U' + a for a in p_args.undefines] if p_args.undefines is not None else []
    config.include_dirs = [os.path.abspath(i) for i in p_args.includes] if p_args.includes is not None else []

    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)

    os.makedirs(config.output_dir)

    impact_analysis_state = ImpactAnalysisRunner(
        config=config,
        disabled=p_args.disable_impact_analysis
    ).run()

    product_state = ProductState(impact_analysis_state=impact_analysis_state)

    product_generator = ProductGenerator(product_state=product_state,
                                         gcc_strategy=gcc_to_tce)

    if not product_generator.is_done():
        product_generator.generate(debug=p_args.debug, params=gcc_params)

    equivalence_res = EquivalenceChecker(product_state=product_state).run()

    operators = []

    for key in equivalence_res['operators'].keys():

        mutants = equivalence_res['operators'][key]['mutants']
        products_total = equivalence_res['operators'][key]['products_total']
        products_compiled = equivalence_res['operators'][key]['products_compiled']
        partially_useless = equivalence_res['operators'][key]['partially_useless']
        totally_useless = equivalence_res['operators'][key]['totally_useless']
        totally_useful = equivalence_res['operators'][key]['totally_useful']
        products_useless = equivalence_res['operators'][key]['products_useless']
        products_useful = equivalence_res['operators'][key]['products_useful']

        operators.append({
            '1_operator': key,
            '2_mutants_total': mutants,
            '3_mutants_partially_useless': partially_useless,
            '4_mutants_totally_useless': totally_useless,
            '5_mutants_totally_useful': totally_useful,
            '6_products_total': products_total,
            '7_products_compiled': products_compiled,
            '8_products_useless': products_useless,
            '9_products_useful': products_useful,
            '__csv': str(key) + ',' + str(mutants) + ',' +
            str(partially_useless) + ', ,' + str(totally_useless) + ', ,' +
            str(totally_useful) + ', ,' + str(products_total) + ',' +
            str(products_compiled) + ',' + str(products_useless) + ', ,' +
            str(products_useful) + ', ,',
        })

    output = {
        '_operators': operators,
        '1_macros': equivalence_res['macros'],
        '2_mutants_total': equivalence_res['total_mutants'],
        '3_mutants_partially_useless': equivalence_res['partially_useless'],
        '4_mutants_totally_useless': equivalence_res['totally_useless'],
        '5_mutants_totally_useful': equivalence_res['totally_useful'],
        '6_products_total': equivalence_res['products_total'],
        '7_products_compiled': equivalence_res['products_compiled'],
        '8_products_useless': equivalence_res['products_useless'],
        '9_products_useful': equivalence_res['products_useful'],
        '__csv': str(equivalence_res['macros']) + ',' + str(equivalence_res['total_mutants']) + ',' +
        str(equivalence_res['partially_useless']) + ', ,' + str(equivalence_res['totally_useless']) + ', ,' +
        str(equivalence_res['totally_useful']) + ', ,' + str(equivalence_res['products_total']) + ',' +
        str(equivalence_res['products_compiled']) + ',' + str(equivalence_res['products_useless']) + ', ,' +
        str(equivalence_res['products_useful']) + ', ,',
    }

    if p_args.verbose:
        print(highlight(
            code=json.dumps(output, indent=2, sort_keys=True),
            lexer=JavascriptLexer(),
            formatter=TerminalFormatter()
        ))

    output_file = os.path.join(config.output_dir, 'result.json')
    print('\nWriting results in %s...' % output_file)
    result = open(output_file, 'w')
    result.write(json.dumps(output, indent=2, sort_keys=True))