import os
import json
import itertools

from tinydb import Query
from pygments import highlight
from pygments.lexers.javascript import JavascriptLexer
from pygments.formatters.terminal import TerminalFormatter

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

    def run(self, verbose=False):
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

                }
            )
            print_progress((i + 1), products_total)
        print(' [DONE]')

        if verbose:
            self._print_result()

    def _print_result(self):
        useful = self.db.all()
        total = 0

        for u in useful:
            total += len(u['useful'])

        output = {
            'useful': useful,
            'total': total
        }

        print(highlight(
            code=json.dumps(output, indent=True, sort_keys=True),
            lexer=JavascriptLexer(),
            formatter=TerminalFormatter()
        ))


def _in(e, d):
    for k in d.keys():
        if e in d[k]:
            return True
    return False
