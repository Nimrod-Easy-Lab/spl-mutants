import datetime
from spl_mutants.impact_analysis.strategies import larissa_braz_strategy, get_macros_strategy


class Runner:

    def __init__(self, impact_analysis=larissa_braz_strategy):
        self.impact_analysis = impact_analysis

    def run(self, file_a, file_b):
        file_a, file_b = _read_files(file_a, file_b)
        return self.impact_analysis(file_a, file_b)

    def run_with_profiling(self, file_a, file_b):
        start_time = datetime.datetime.now()
        return self.run(file_a, file_b), datetime.datetime.now() - start_time

    def get_macros(self, file_a):
        return get_macros_strategy(open(file_a, "rt").readlines())


def _read_files(file_a, file_b):
    return (open(file_a, "rt").readlines(),
            open(file_b, "rt").readlines())
