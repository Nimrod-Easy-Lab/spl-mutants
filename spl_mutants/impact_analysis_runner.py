from spl_mutants.db.impact_analisys_state import ImpactAnalysisState
from spl_mutants.db.state import State
from spl_mutants.impact_analysis.runner import Runner


class ImpactAnalysisRunner:

    def __init__(self, config):
        self.impact_analysis_state = ImpactAnalysisState(
            state=State(config=config))
        self.mutants = self.impact_analysis_state.get_mutants()
        self.original_program = self.impact_analysis_state.get_source_file()
        self.runner = Runner()

    def run(self):
        for mutant in self.mutants:
            result = self.runner.run(self.original_program, mutant.get('file'))
            self.impact_analysis_state.set_impact_analysis(mutant=mutant,
                                                           result=result)

        return self.impact_analysis_state
