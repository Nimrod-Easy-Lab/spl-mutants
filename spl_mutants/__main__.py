import os
import shutil

from spl_mutants.state import StateConfig, State
from spl_mutants.impact_analysis_runner import ImpactAnalysisRunner

def main():
    config = StateConfig()

    config.output_dir = os.path.abspath('../tests/examples/test_c/mutants'
                                        '/output')
    config.mutants_dir = os.path.abspath('../tests/examples/test_c/mutants')
    config.source_file = os.path.abspath('../tests/examples/test_c/test.c')

    if os.path.exists(config.output_dir):
        shutil.rmtree(config.output_dir)

    os.mkdir(config.output_dir)

    state = State(config=config)

    ImpactAnalysisRunner(state=state).run()

    print(state.get_mutants())

if __name__ == '__main__':
    main()
