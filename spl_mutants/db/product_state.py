

class ProductState:

    def __init__(self, impact_analysis_state):
        self.impact_analysis_state = impact_analysis_state
        self.state = impact_analysis_state.state
        self.db = self.state.db.table('products')
        self._set_products_table()

    def _set_products_table(self):
        mutants = self.impact_analysis_state.get_mutants()

        for mutant in mutants:
            file = mutant['file']
            name = mutant['name']
            operator = mutant['operator']
            products = mutant['impact_analysis']['impacted_products']

            for product in products:
                product_name = self.get_product_name(product)


    def gen_product_name(self, features):
        return 'a'