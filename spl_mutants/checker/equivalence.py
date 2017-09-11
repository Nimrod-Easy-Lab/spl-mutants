import os
import json

from tinydb import Query
from pygments import highlight
from pygments.lexers.javascript import JavascriptLexer
from pygments.formatters.terminal import TerminalFormatter

from spl_mutants.checker.common import get_filename, diff


class EquivalenceChecker:

    def __init__(self, product_state):
        self.product_state = product_state
        self.impact_analysis_state = product_state.impact_analysis_state
        self.state = self.impact_analysis_state.state
        self.products_db = self.state.db.table('products')
        self.db = self.state.db.table('equivalence')

    def run(self, verbose=False):
        products = self.products_db.all()

        for product in products:
            product_dir = os.path.join(self.state.products_dir,
                                       product['product_code'])
            original_product = os.path.join(
                product_dir, get_filename(self.state.source_file))

            for mutant in product['mutants']:
                mutant_product = os.path.join(
                    product_dir, get_filename(mutant['file']))
                diff_result = diff(
                    ['diff', '--binary', original_product, mutant_product])

                self.db.insert(
                    {
                        'name': mutant['name'],
                        'operator': mutant['operator'],
                        'file': mutant['file'],
                        'product': product['features'],
                        'product_code': product['product_code'],
                        'useless': diff_result[0]
                    }
                )

        if verbose:
            self._print_result()

    def _print_result(self):
        output = {
            'total_mutants':
                len(self.state.db.table('mutants').all()),
            'products_total':
                self.state.db.search(
                    Query().type == 'config')[0]['products'],
            'products_impacted':
                self.state.db.search(
                    Query().type == 'config')[0]['products_impacted'],
            'products_useful':
                len(self.state.db.table('equivalence').search(
                    Query().useless == False)),
            'products_equivalent':
                len(self.state.db.table('equivalence').search(
                    Query().useless == True))
        }

        print('\n=== EQUIVALENCE CHECKER ===')

        print(highlight(
            code=json.dumps(output, indent=True, sort_keys=True),
            lexer=JavascriptLexer(),
            formatter=TerminalFormatter()
        ))

