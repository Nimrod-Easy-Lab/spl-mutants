from spl_mutants.db.impact_analisys_state import ImpactAnalysisState
from spl_mutants.db.state import State
from spl_mutants.impact_analysis.runner import Runner
from spl_mutants.util import print_progress


class ImpactAnalysisRunner:

    def __init__(self, config, disabled=False):
        self.impact_analysis_state = ImpactAnalysisState(
            state=State(config=config), disabled=disabled)
        self.mutants = self.impact_analysis_state.get_mutants()
        self.original_program = self.impact_analysis_state.get_source_file()
        self.runner = Runner()
        self.disabled = disabled

    def run(self):

        total_mutants = len(self.mutants)

        if not self.disabled:
            print('Starting impact analysis for %i mutants...' % total_mutants)
        for i, mutant in enumerate(self.mutants):
            result = self.runner.run(self.original_program, mutant.get('file'))
            self.impact_analysis_state.set_impact_analysis(mutant=mutant,
                                                           result=result)
            print_progress((i + 1), total_mutants) if not self.disabled else None
        if not self.disabled:
            print(' [DONE]')

        return self.impact_analysis_state
