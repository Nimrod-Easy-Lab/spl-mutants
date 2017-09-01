import os
import sys
import itertools

from tinydb import TinyDB, Query
from tinydb.operations import set


class StateConfig:

    state_file = 'state.json'
    source_file = None
    source_dir = None
    mutants_dir = None
    output_dir = None
    include_dirs = []


class State:

    def __init__(self, config):
        self.db = TinyDB(os.path.join(config.output_dir, config.state_file))

        self.config = config
        self.db.insert({
            'source_dir': config.source_dir,
            'source_file': config.source_file,
            'include_dirs': config.include_dirs,
            'output_dir': config.output_dir,
            'mutants_dir': config.mutants_dir
        })

        self._set_mutants_table(config.mutants_dir)
        self.db.table('products')

    def _get_state(self):
        return self.db.all()[0]

    def get_mutants(self):
        return self.db.table('mutants').all()

    def get_source_file(self):
        return self._get_state().get('source_file')

    def set_impact_analysis(self, mutant, result):
        self.db.table("mutants").update(
            set('impact_analysis', {
                'impacted_features': result.impacted_macros,
                'impacted_products': _impacted_products(result.impacted_macros)
            }),
            Query().name == mutant.get('name'))

    def _set_mutants_table(self, path):
        mutants = self.db.table('mutants')

        mutant_files = [file for file in os.listdir(path)
                        if (os.path.isfile(os.path.join(path, file))
                            and (file.endswith('.c')
                                 or file.endswith('.h')))]

        for file in mutant_files:
            mutants.insert(
                {
                    'name': _extract_mutant_name(file=file),
                    'operator': _extract_mutant_operator(file=file),
                    'file': os.path.join(path, file)
                }
            )

        return mutants


def _extract_mutant_name(file):
    try:
        parts = file.replace('.c', '').replace('.h', '').split('_')
        return '%s_%s' % (parts[-2], parts[-1])
    except IndexError:
        print('\n\033[91m\033[1m'
              'error: file name {file} not follow the convention '
              'filename_OPERATOR_ID.ext'.format(file=file), file=sys.stderr)
        sys.exit(1)


def _extract_mutant_operator(file):
    try:
        parts = file.replace('.c', '').replace('.h', '').split('_')
        return parts[-2]
    except IndexError:
        print('\n\033[91m\033[1m'
              'error: file name {file} not follow the convention '
              'filename_OPERATOR_ID.ext'.format(file=file), file=sys.stderr)
        sys.exit(1)


def _impacted_products(impacted_features):
    combinations_params = []

    for i in range(len(impacted_features) + 1):
        for combination in itertools.combinations(impacted_features, i):
            combinations_params.append(combination)

    return combinations_params
