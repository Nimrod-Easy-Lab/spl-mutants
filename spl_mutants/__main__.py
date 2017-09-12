import os
import shutil

from spl_mutants.db.state import Config
from spl_mutants.db.product_state import ProductState
from spl_mutants.impact_analysis_runner import ImpactAnalysisRunner
from spl_mutants.products.product_generator import ProductGenerator
from spl_mutants.products.gcc_strategies import gcc_to_tce
from spl_mutants.checker.equivalence import EquivalenceChecker
from spl_mutants.checker.duplicate import DuplicateChecker


def main():
    config = Config()

    config.output_dir = os.path.abspath('/home/marcioaug/Projects/marcioaug/'
                                        'spl-mutants/tests/examples/ssl_asn1_c'
                                        '/all_macros')
    config.mutants_dir = os.path.abspath('/home/marcioaug/Projects/marcioaug/'
                                         'mutants/openssl/ssl/ssl_asn1_c')
    # config.source_file = os.path.abspath('/home/marcioaug/Projects/marcioaug/'
    #                                      'spl-mutants/tests/examples/test8_c/'
    #                                      'test.c')

    config.source_file = os.path.abspath('/home/marcioaug/Projects/marcioaug/'
                                         'openssl/ssl/ssl_asn1.c')

    config.include_dirs = []
    config.include_dirs.append('/home/marcioaug/Projects/marcioaug/openssl/include')
    config.include_dirs.append('/home/marcioaug/Projects/marcioaug/openssl/crypto/include')
    config.include_dirs.append('/home/marcioaug/Projects/marcioaug/openssl')

    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)

    os.mkdir(config.output_dir)

    impact_analysis_state = ImpactAnalysisRunner(config=config).run()

    product_state = ProductState(impact_analysis_state=impact_analysis_state)

    product_generator = ProductGenerator(product_state=product_state,
                                         gcc_strategy=gcc_to_tce)

    if not product_generator.is_done():
        product_generator.generate()

    EquivalenceChecker(product_state=product_state).run(verbose=True)
    DuplicateChecker(product_state=product_state).run(verbose=True)


if __name__ == '__main__':
    main()
