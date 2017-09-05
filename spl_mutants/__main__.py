import os
import shutil

from tinydb import Query

from spl_mutants.db.state import Config, State
from spl_mutants.db.impact_analisys_state import ImpactAnalysisState
from spl_mutants.db.product_state import ProductState
from spl_mutants.impact_analysis_runner import ImpactAnalysisRunner
from spl_mutants.products.product_generator import ProductGenerator
from spl_mutants.products.gcc_strategies import gcc_to_tce
from spl_mutants.checker.equivalence import EquivalenceChecker


def main():
    config = Config()

    config.output_dir = os.path.abspath('/home/marcioaug/Projects/marcioaug/mutants/openssl/ssl/methods_c'
                                        '/output')
    config.mutants_dir = os.path.abspath('/home/marcioaug/Projects/marcioaug/mutants/openssl/ssl/methods_c')
    config.source_file = os.path.abspath('/home/marcioaug/Projects/marcioaug/openssl/ssl/methods.c')

    config.include_dirs = []
    config.include_dirs.append('/home/marcioaug/Projects/marcioaug/openssl/include')
    config.include_dirs.append('/home/marcioaug/Projects/marcioaug/openssl')

    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)

    os.mkdir(config.output_dir)

    state = State(config=config)
    impact_analysis_state = ImpactAnalysisState(state=state)

    ImpactAnalysisRunner(state=impact_analysis_state).run()

    product_state = ProductState(impact_analysis_state=impact_analysis_state)
    product_generator = ProductGenerator(product_state=product_state,
                                         gcc_strategy=gcc_to_tce)

    product_generator.generate()

    equivalence_checker = EquivalenceChecker(product_state=product_state)

    equivalence_checker.run()

    output = {
        'total_mutants': len(state.db.table('mutants').all()),
        'products_total_to_test': state.db.search(Query().type == 'config')[0]['all_to_test'],
        'products_impacted': state.db.search(Query().type == 'config')[0]['product_versions'],
        'products_useful': len(state.db.table('equivalence').search(Query().useless == False)),
        'products_useless': len(state.db.table('equivalence').search(Query().useless == True))
    }

    print(output)

if __name__ == '__main__':
    main()
