import os

from tinydb import Query

from spl_mutants.checker.common import get_filename, diff
from spl_mutants.util import pprint_progress, print_progress

import json

class EquivalenceChecker:

    def __init__(self, product_state):
        self.product_state = product_state
        self.impact_analysis_state = product_state.impact_analysis_state
        self.state = self.impact_analysis_state.state
        self.products_db = self.state.db.table('products')
        self.db = self.state.db.table('equivalence')

    def run(self, verbose=False):
        products = self.products_db.all()

        print('Checking equivalence...')
        products_total = len(products)
        for i, product in enumerate(products):
            product_dir = os.path.join(self.state.products_dir,
                                       product['product_code'])
            original_product = os.path.join(
                product_dir, get_filename(self.state.source_file))

            mutants_total = len(product['mutants'])
            for j, mutant in enumerate(product['mutants']):
                mutant_product = os.path.join(
                    product_dir, get_filename(mutant['file']))

                diff_result = [True]
                compile_error = True
                invalid_configuration = True

                if os.path.exists(original_product):
                    invalid_configuration = False
                    if os.path.exists(mutant_product):
                        compile_error = False
                        diff_result = diff(
                            ['diff', '--binary', original_product, mutant_product])

                self.db.insert(
                    {
                        'name': mutant['name'],
                        'operator': mutant['operator'],
                        'file': mutant['file'],
                        'product': product['features'],
                        'product_code': product['product_code'],
                        'useless': diff_result[0],
                        'compile_error': compile_error,
                        'invalid_configuration': invalid_configuration
                    }
                )

                pprint_progress((i + 1), products_total, (j + 1), mutants_total)
            print_progress((i + 1), products_total)
        print(' [DONE]')

        return self._collect_result()

    def _collect_result(self):

        useful = self.state.db.table('equivalence').search(
                    Query().useless == False)

        useful_to_print = []

        for mutant in useful:
            useful_to_print.append(
                {
                    'product_code': mutant['product_code'],
                    'name': mutant['name'],
                    'product': mutant['product']
                }
            )
    
        mutants = self.state.db.table('equivalence').all()

        mutants_to_print = {}
        operators = {}
        mutants_status = {}

        for mutant in mutants:
            if mutant['product_code'] not in mutants_to_print.keys():
                mutants_to_print[mutant['product_code']] = {
                    'useless': [],
                    'useful': [],
                    'invalid_configuration': mutant['invalid_configuration'],
                    'useless_total': 0,
                    'useful_total': 0
                }

            if mutant['operator'] not in operators.keys():
                operators[mutant['operator']] = {
                    'useless': 0,
                    'useful': 0,
                    'not_compile': 0,
                    'compile': 0
                }

            if mutant['name'] not in mutants_status.keys():
                mutants_status[mutant['name']] = {
                    'name': mutant['name'],
                    'operator': mutant['operator'],
                    'useless': 0,
                    'useful': 0,
                    'not_compile': 0,
                    'compile': 0
                }

            if not mutant['compile_error']:
                if mutant['useless']:
                    mutants_to_print[
                        mutant['product_code']
                    ]['useless'].append(mutant['name'])
                    mutants_to_print[
                        mutant['product_code']
                    ]['useless_total'] += 1
                    operators[mutant['operator']]['useless'] += 1
                    mutants_status[mutant['name']]['useless'] += 1
                else:
                    mutants_to_print[
                        mutant['product_code']
                    ]['useful'].append(mutant['name'])
                    mutants_to_print[
                        mutant['product_code']
                    ]['useful_total'] += 1
                    operators[mutant['operator']]['useful'] += 1
                    mutants_status[mutant['name']]['useful'] += 1
                operators[mutant['operator']]['compile'] += 1
                mutants_status[mutant['name']]['compile'] += 1
            else:
                operators[mutant['operator']]['not_compile'] += 1
                mutants_status[mutant['name']]['not_compile'] += 1

        compiled_products = 0
        products_not_equivalent = len(self.state.db.table('equivalence').search(
            Query().useless == False))

        for product_code in mutants_to_print.keys():
            useless_total = mutants_to_print[product_code]['useless_total']
            useful_total = mutants_to_print[product_code]['useful_total']
            mutants_compiled = useless_total + useful_total
            reduction = 0

            if mutants_compiled != 0:
                reduction = 1 - (useful_total / mutants_compiled)

            mutants_to_print[product_code]['mutants_compiled'] = mutants_compiled
            mutants_to_print[product_code]['reduction'] = reduction
            compiled_products += mutants_to_print[product_code]['mutants_compiled']

        totally_useless = []
        totally_useful = []
        operators_table = {}
        partially_useless = []

        for key in mutants_status.keys():
            if mutants_status[key]['compile'] == mutants_status[key]['useless']:
                totally_useless.append(mutants_status[key])
            elif mutants_status[key]['compile'] == mutants_status[key]['useful']:
                totally_useful.append(mutants_status[key])
            else:
                partially_useless.append(mutants_status[key])

        for key in operators.keys():
            operators_table[key] = {
                'mutants': len(self.state.db.table('mutants').search(
                    Query().operator == key)),
                'totally_useless': len([m for m in totally_useless if m['operator'] == key]),
                'totally_useful': len([m for m in totally_useful if m['operator'] == key]),
                'products_total': operators[key]['compile'] + operators[key]['not_compile'],
                'products_compiled': operators[key]['compile'],
                'partially_useless': len([m for m in partially_useless if m['operator'] == key]),
                'products_useless': operators[key]['useless'],
                'products_useful': operators[key]['useful'],
            }

        return {
            'macros': len(self.state.db.search(
                    Query().type == 'config')[0]['macros']),
            'total_mutants':
                len(self.state.db.table('mutants').all()),
            'products_total':
                self.state.db.search(
                    Query().type == 'config')[0]['products'],
            'products_compiled': compiled_products,
            'totally_useless': len(totally_useless),
            'totally_useful': len(totally_useful),
            'operators': operators_table,
            'partially_useless': len(partially_useless)
        }

