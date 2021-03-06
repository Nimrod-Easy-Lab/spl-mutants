import os

from tinydb import Query

from spl_mutants.checker.common import get_filename, diff
from spl_mutants.util import pprint_progress, print_progress


class DuplicateChecker:

    def __init__(self, product_state):
        self.product_state = product_state
        self.impact_analysis_state = product_state.impact_analysis_state
        self.state = self.impact_analysis_state.state
        self.products_db = self.state.db.table('products')
        self.db = self.state.db.table('duplicate')
        self.equivalence_db = self.state.db.table('equivalence')

    def run(self):
        products = self.products_db.all()
        products_total = len(products)
        equals = {}

        print('Checking duplicates...')
        for i, product in enumerate(products):
            product_dir = os.path.join(self.state.products_dir,
                                       product['product_code'])

            useful_mutants = self.equivalence_db.search(
                (Query().product_code == product['product_code']) &
                (Query().useless == False))
            mutants_total = len(useful_mutants)
            equals[product['product_code']] = {}

            for j, mutant_a in enumerate(useful_mutants):

                if not _in(mutant_a['name'], equals[product['product_code']]):
                    equals[product['product_code']][mutant_a['name']] = []

                    for mutant_b in useful_mutants:
                        if mutant_b['name'] != mutant_a['name']:
                            mutant_a_product = os.path.join(
                                product_dir, get_filename(mutant_a['file']))
                            mutant_b_product = os.path.join(
                                product_dir, get_filename(mutant_b['file']))

                            if (os.path.exists(mutant_a_product)
                               and os.path.exists(mutant_b_product)):
                                diff_result = diff(
                                    ['diff', '--binary', mutant_a_product,
                                     mutant_b_product])

                                if diff_result[0]:
                                    equals[product['product_code']][mutant_a['name']].append(mutant_b['name'])
                pprint_progress((i + 1), products_total, (j + 1), mutants_total)

            self.db.insert(
                {
                    'product_code': product['product_code'],
                    'configuration': product['features'],
                    'useful': list(equals[product['product_code']].keys()),
                    'duplicates': equals[product['product_code']]
                }
            )
            print_progress((i + 1), products_total)
        print(' [DONE]')

        return self._collect_result()

    def _collect_result(self):
        useful = self.db.all()
        total = 0
        duplicate_set = []
        duplicate_status = {}

        for u in useful:
            total += len(u['useful'])
            for d in u['duplicates'].keys():
                duplicate_set.append(u['duplicates'][d] + [d])

        for s in duplicate_set:
            for m in s:
                if m not in duplicate_status.keys():
                    duplicate_status[m] = {
                        'duplicate': 0,
                        'not_duplicate': 0
                    }
                if len(s) > 1:
                    duplicate_status[m]['duplicate'] += 1
                else:
                    duplicate_status[m]['not_duplicate'] += 1

        totally_useless = 0
        totally_useful = 0
        partially_useless = 0
        operators = {}

        for key in duplicate_status.keys():

            mutant = self.state.db.table('mutants').search(
                    Query().name == key)[0]

            operator = mutant['operator']

            if operator not in operators.keys():
                operators[operator] = {
                    'totally_useless': 0,
                    'totally_useful': 0,
                    'partially_useless': 0,
                    'products_useless': 0,
                    'products_useful': 0
                }

            operators[operator]['products_useless'] += duplicate_status[key]['duplicate']
            operators[operator]['products_useful'] += duplicate_status[key]['not_duplicate']

            if duplicate_status[key]['not_duplicate'] == 0:
                totally_useless += 1
                operators[operator]['totally_useless'] += 1
            elif duplicate_status[key]['duplicate'] == 0:
                totally_useful += 1
                operators[operator]['totally_useful'] += 1
            else:
                partially_useless += 1
                operators[operator]['partially_useless'] += 1

        return {
            'operators': operators,
            'totally_useless': totally_useless,
            'totally_useful': totally_useful,
            'partially_useless': partially_useless,
            'products_useful': total
        }


def _in(e, d):
    for k in d.keys():
        if e in d[k]:
            return True
    return False
