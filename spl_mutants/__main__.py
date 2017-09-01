import os
import shutil

from spl_mutants.db.impact_analisys_state import ImpactAnalysisState
from spl_mutants.db.state import Config, State
from spl_mutants.impact_analysis_runner import ImpactAnalysisRunner


def main():
    config = Config()

    config.output_dir = os.path.abspath('../tests/examples/test_c/mutants'
                                        '/output')
    config.mutants_dir = os.path.abspath('../tests/examples/test_c/mutants')
    config.source_file = os.path.abspath('../tests/examples/test_c/test.c')

    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)

    os.mkdir(config.output_dir)

    state = State(config=config)
    impact_analysis_state = ImpactAnalysisState(state=state)

    print(state.output_dir)

    ImpactAnalysisRunner(state=impact_analysis_state).run()

    print(impact_analysis_state.get_mutants())

if __name__ == '__main__':
    main()
