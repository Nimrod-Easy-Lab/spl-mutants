import os
import sys

from tinydb import Query
from tinydb.operations import set, add


class ImpactAnalysisState:

    def __init__(self, state, disabled=False):
        self.state = state
        self.db = state.db.table('mutants')
        self._set_mutants_table(state.mutants_dir)
        self.disabled = disabled

    def get_mutants(self):
        return self.db.all()

    def get_source_file(self):
        return self.state.source_file

    def set_impact_analysis(self, mutant, result):

        if self.disabled:
            impacted_macros = result.all_macros
        else:
            impacted_macros = result.impacted_macros

        self.db.update(
            set('impact_analysis', {
                'impacted_features': impacted_macros,
                'not_impacted_features': [feature for feature in
                                          result.all_macros if feature not in
                                          impacted_macros],
                'all_features': result.all_macros,
                'all_features_len': len(result.all_macros),
                'elapsed_time': str(result.elapsed_time)
            }),
            Query().name == mutant.get('name'))

        self.state.db.update(
            add('products', 2 ** len(result.all_macros)),
            Query().type == 'config'
        )

        self.state.db.update(
            add('products_impacted', 2**len(impacted_macros)),
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

