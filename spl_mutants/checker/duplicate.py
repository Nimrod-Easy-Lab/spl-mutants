import os
import json
import itertools

from tinydb import Query
from pygments import highlight
from pygments.lexers.javascript import JavascriptLexer
from pygments.formatters.terminal import TerminalFormatter

from spl_mutants.checker.common import get_filename, diff


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

        for product in products:
            product_dir = os.path.join(self.state.products_dir,
                                       product['product_code'])

            useful_mutants = self.equivalence_db.search(
                (Query().product_code == product['product_code']) &
                (Query().useless == False))

            for mutants in itertools.combinations(useful_mutants, 2):
                mutant_a = mutants[0]
                mutant_b = mutants[1]

                mutant_a_product = os.path.join(
                    product_dir, get_filename(mutant_a['file']))
                mutant_b_product = os.path.join(
                    product_dir, get_filename(mutant_b['file']))

                diff_result = diff(
                    ['diff', '--binary', mutant_a_product,
                     mutant_b_product])

                self.db.insert(
                    {
                        'mutant_a': {
                            'file': mutant_a['file'],
                            'name': mutant_a['name'],
                            'operator': mutant_a['operator']
                        },
                        'mutant_b': {
                            'file': mutant_b['file'],
                            'name': mutant_b['name'],
                            'operator': mutant_b['operator']
                        },
                        'product': product['features'],
                        'product_code': product['product_code'],
                        'duplicate': diff_result[0]
                    }
                )

        if verbose:
            self._print_result()

    def _print_result(self):
        output = {
            'products_duplicate':
                len(self.db.search(Query().duplicate == True))
        }

        print('\n=== DUPLICATE CHECKER ===')

        print(highlight(
            code=json.dumps(output, indent=True, sort_keys=True),
            lexer=JavascriptLexer(),
            formatter=TerminalFormatter()
        ))
