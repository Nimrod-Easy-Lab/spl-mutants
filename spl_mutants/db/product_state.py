import hashlib

from tinydb import Query
from tinydb.operations import increment

from spl_mutants.db.operations import append


class ProductState:

    def __init__(self, impact_analysis_state):
        self.impact_analysis_state = impact_analysis_state
        self.state = impact_analysis_state.state
        self.db = self.state.db.table('products')
        self._set_products_table()

    def _set_products_table(self):
        mutants = self.impact_analysis_state.get_mutants()

        for mutant in mutants:
            products = mutant['impact_analysis']['impacted_products']

            for product in products:
                product_code = _gen_product_code(product)

                has_product_code = len(
                    self.db.search(Query().product_code == product_code)) > 0

                self.state.db.update(
                    increment('product_versions'),
                    Query().type == 'config'
                )

                if has_product_code:
                    self.db.update(append('mutants', _mutant_dict(mutant)),
                                   Query().product_code == product_code)

                else:
                    self.db.insert({
                        'product_code': product_code,
                        'features': product,
                        'mutants': [_mutant_dict(mutant)]
                    })


def _mutant_dict(mutant):
    return {
        'name': mutant['name'],
        'operator': mutant['operator'],
        'file': mutant['file']
    }


def _gen_product_code(features):
    return hashlib.md5(str(features).encode('utf-8')).hexdigest()
