import os
import sys
import itertools

from tinydb import Query
from tinydb.operations import set, add


class ImpactAnalysisState:

    def __init__(self, state):
        self.state = state
        self.db = state.db.table('mutants')
        self._set_mutants_table(state.mutants_dir)

    def get_mutants(self):
        return self.db.all()

    def get_source_file(self):
        return self.state.source_file

    def set_impact_analysis(self, mutant, result):

        impacted_products = _impacted_products(result.impacted_macros)

        self.db.update(
            set('impact_analysis', {
                'impacted_features': result.impacted_macros,
                'impacted_products': impacted_products,
                'all_features': result.all_macros,
                'all_features_len': len(result.all_macros),
                'elapsed_time': str(result.elapsed_time)
            }),
            Query().name == mutant.get('name'))

        self.state.db.update(
            add('all_to_test', 2**len(result.all_macros)),
            Query().type == 'config'
        )

    def _set_mutants_table(self, path):
        mutant_files = [file for file in os.listdir(path)
                        if (os.path.isfile(os.path.join(path, file))
                            and (file.endswith('.c')
                                 or file.endswith('.h')))]

        for file in mutant_files:
            self.db.insert(
                {
                    'name': _extract_mutant_name(file=file),
                    'operator': _extract_mutant_operator(file=file),
                    'file': os.path.join(path, file)
                }
            )


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
