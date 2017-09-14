import os
import shutil
import argparse

from spl_mutants.db.state import Config
from spl_mutants.db.product_state import ProductState
from spl_mutants.impact_analysis_runner import ImpactAnalysisRunner
from spl_mutants.products.product_generator import ProductGenerator
from spl_mutants.products.gcc_strategies import gcc_to_tce
from spl_mutants.checker.equivalence import EquivalenceChecker
from spl_mutants.checker.duplicate import DuplicateChecker


def main():
    config = Config()

    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--source_file', type=str, required=True)
    parser.add_argument('-M', '--mutants_dir', type=str, required=True)
    parser.add_argument('-O', '--output_dir', type=str, required=True)
    parser.add_argument('-I', '--includes', nargs='*')
    parser.add_argument('-v', '--verbose', default=False, action='store_true')
    parser.add_argument('-D', '--debug', default=False, action='store_true')
    parser.add_argument('--disable-impact-analysis', default=False, action='store_true')
    parser.add_argument('--no-check-duplicates', default=False, action='store_true')

    p_args = parser.parse_args()

    config.include_dirs = []
    config.output_dir = os.path.abspath(p_args.output_dir)
    config.mutants_dir = os.path.abspath(p_args.mutants_dir)
    config.source_file = os.path.abspath(p_args.source_file)
    config.include_dirs = [os.path.abspath(i) for i in p_args.includes]

    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)

    os.makedirs(config.output_dir)

    impact_analysis_state = ImpactAnalysisRunner(
        config=config,
        disabled=p_args.disable_impact_analysis
    ).run()

    product_state = ProductState(impact_analysis_state=impact_analysis_state)

    product_generator = ProductGenerator(product_state=product_state,
                                         gcc_strategy=gcc_to_tce)

    if not product_generator.is_done():
        product_generator.generate(debug=p_args.debug)

    EquivalenceChecker(product_state=product_state).run(verbose=p_args.verbose)
    if not p_args.no_check_duplicates:
        DuplicateChecker(product_state=product_state).run(verbose=p_args.verbose)
