from spl_mutants.impact_analysis.runner import Runner


class ImpactAnalysisRunner:

    def __init__(self, state):
        self.state = state
        self.mutants = state.get_mutants()
        self.original_program = state.get_source_file()
        self.runner = Runner()

    def run(self):
        for mutant in self.mutants:
            result = self.runner.run_with_profiling(self.original_program,
                                                    mutant.get('file'))
            self.state.set_impact_analysis(mutant=mutant, result=result[0])

