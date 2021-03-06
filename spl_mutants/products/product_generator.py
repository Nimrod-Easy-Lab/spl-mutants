import os
from tinydb import Query
from tinydb.operations import set

from spl_mutants.products.gcc_strategies import GCCConfig, Executor
from spl_mutants.util import print_progress, pprint_progress


class ProductGenerator:

    def __init__(self, product_state, gcc_strategy):
        self.product_state = product_state
        self.impact_analysis_state = product_state.impact_analysis_state
        self.state = self.impact_analysis_state.state
        self.products_db = self.state.db.table('products')
        self.db = self.state.db.table('mutants_gen')
        self.gcc_strategy = gcc_strategy

        self._setup()

    def _setup(self):
        products = self.products_db.all()
        output_dir = os.path.join(self.state.output_dir, 'products')

        self.state.db.update(set('products_dir', output_dir), Query().type == 'config')

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        products_total = len(products)
        print('Preparing generation for %s configurations...' % products_total)
        for i, product in enumerate(products):
            product_dir = os.path.join(output_dir, product['product_code'])

            if not os.path.exists(product_dir):
                os.mkdir(product_dir)

            original = {
                'operator': 'ORIGINAL',
                'file': self.state.source_file,
                'name': 'ORIGINAL_0'
            }

            self.db.insert(_initialize_mutant(original, product, product_dir))

            mutants_total = len(product['mutants'])

            for j, mutant in enumerate(product['mutants']):
                self.db.insert(_initialize_mutant(mutant, product, product_dir))
                pprint_progress((i + 1), products_total, (j + 1), mutants_total)
            print_progress((i + 1), products_total)
        print(' [DONE]')

    def is_done(self):
        return (len(self.db.all()) > 0 and
                len(self.db.search(Query().generated == False)) == 0)

    def generate(self, params=None, verbose=False, debug=False):
        mutants = self.db.all()
        mutants_total = len(mutants)

        print('Starting generation for %s products...' % mutants_total)
        for i, mutant in enumerate(mutants):
            if not mutant['generated']:
                config = GCCConfig()

                if not params:
                    config.params = []
                else:
                    config.params = list(params)

                config.params += _get_i_params(self.state.include_dirs)
                config.params += _get_d_params(mutant['features'])
                config.output_file = mutant['output_file']
                config.input_file = mutant['file']
                config.source_file = self.state.source_file

                Executor(config=config,
                         strategy=self.gcc_strategy).run(log=debug)
                self.db.update(
                    set('generated', True),
                    (Query().name == mutant['name']) &
                    (Query().product_code == mutant['product_code'])
                )

            print_progress(i + 1, mutants_total)
        print(' [DONE]')


def _initialize_mutant(mutant, product, product_dir):
    mutant['generated'] = False
    mutant['product_code'] = product['product_code']
    mutant['features'] = product['features']
    mutant['output_file'] = os.path.join(product_dir,
                                         get_output_filename(mutant['file']))

    return mutant


def _replace_extension(s, ext):
    index = s.rfind('.')
    return s[:index] + '.{ext}'.format(ext=ext)


def get_output_filename(file):
    return _replace_extension(_get_filename(file), 'out')


def _get_filename(file):
    return str(file).split(os.sep)[-1]


def _get_d_params(features):
    return ['-D{feature}'.format(feature=feature) for feature in features]


def _get_i_params(includes):
    return ['-I{include}'.format(include=include) for include in includes]

