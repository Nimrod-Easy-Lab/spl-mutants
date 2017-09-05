import os
import subprocess

from spl_mutants.products.product_generator import get_output_filename


class EquivalenceChecker:

    def __init__(self, product_state):
        self.product_state = product_state
        self.impact_analysis_state = product_state.impact_analysis_state
        self.state = self.impact_analysis_state.state
        self.products_db = self.state.db.table('products')
        self.db = self.state.db.table('equivalence')

    def run(self):
        products = self.products_db.all()

        for product in products:
            product_dir = os.path.join(self.state.products_dir,
                                       product['product_code'])
            original_product = os.path.join(
                product_dir, _get_filename(self.state.source_file))

            for mutant in product['mutants']:
                mutant_product = os.path.join(
                    product_dir, _get_filename(mutant['file']))
                diff = _diff(
                    ['diff', '--binary', original_product, mutant_product])

                self.db.insert(
                    {
                        'name': mutant['name'],
                        'operator': mutant['operator'],
                        'file': mutant['file'],
                        'product': product['features'],
                        'product_code': product['product_code'],
                        'useless': diff[0]
                    }
                )


def _get_filename(file):
    return get_output_filename(file)


def _diff(command_line):
    output = subprocess.getstatusoutput(' '.join(command_line))

    if output[0] == 0:
        return True, output
    else:
        return False, output
