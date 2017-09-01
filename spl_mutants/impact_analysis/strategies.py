from spl_mutants.impact_analysis.braz import Braz


def larissa_braz_strategy(file_a, file_b):
    return Braz(file_a, file_b).run(verbose=False)
