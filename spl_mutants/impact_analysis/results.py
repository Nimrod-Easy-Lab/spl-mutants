class ImpactAnalysisResult:

    def __init__(self):
        self.macros_file = []
        self.lines_start = []
        self.lines_end = []
        self.impacted_macros = []
        self.changed_lines = []
        self.all_macros = []
        self.changes = None
        self.file_a = None
        self.file_b = None
        self.enough_combinations = []
        self.all_combinations = []
        self.useless_combinations = []
        self.useless_products = []
        self.useful_products = []
        self.impact_analysis_time = None
        self.compile_time = None
        self.diff_time = None
