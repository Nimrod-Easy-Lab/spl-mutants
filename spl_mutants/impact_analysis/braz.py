import re
import datetime

from spl_mutants.impact_analysis.utils.utils import append_if_not_in

from spl_mutants.impact_analysis.results import ImpactAnalysisResult
from spl_mutants.impact_analysis.utils.diff import changed_lines
from spl_mutants.impact_analysis.utils.diff import get_changes


class Braz:

    def __init__(self, old_code, new_code):
        self.old_code = old_code
        self.new_code = new_code

    def _run(self):
        result = ImpactAnalysisResult()

        result.changes = get_changes(self.old_code, self.new_code)
        result.changed_lines = changed_lines(self.old_code, self.new_code)

        self._find_macro_lines(self.new_code, result)
        self._get_all_macros(result)
        self._get_changed_macros(result)

        return result

    def _run_no_reverse(self, verbose=False):
        result = self._run()

        if verbose:
            self._verbose(result)

        return result

    def run(self, verbose=False):
        start_time = datetime.datetime.now()
        result = self._run()

        self._union_with_reverse_analysis(result)
        result.elapsed_time = datetime.datetime.now() - start_time
        if verbose:
            self._verbose(result)

        return result

    def _union_with_reverse_analysis(self, result):
        reverse_analysis = Braz(self.new_code, self.old_code)._run_no_reverse()
        result.all_macros = append_if_not_in(
            from_list=reverse_analysis.all_macros,
            to_list=result.all_macros
        )
        result.impacted_macros = append_if_not_in(
            from_list=reverse_analysis.impacted_macros,
            to_list=result.impacted_macros
        )

    def _find_macro_lines(self, file, result):
        stack_macros = []
        stack_lines = []
        line = 1
        for l in file:
            l = re.sub(r'# +', '#', l)
            if l.strip().startswith('#if'):
                stack_macros.append(l)
                stack_lines.append(line)
            elif l.strip().startswith('#endif'):
                if len(stack_macros) != 0:
                    result.macros_file.append(stack_macros.pop())
                    result.lines_start.append(stack_lines.pop())
                    result.lines_end.append(line)
            line += 1

    def _get_changed_macros(self, result):
        for line in result.changed_lines:
            for i, ls in enumerate(result.lines_start):
                if result.lines_end[i] >= line >= ls:
                    macros = self._get_macros_in_line(result.macros_file[i])
                    if macros:
                        append_if_not_in(result.impacted_macros, macros)
                        append_if_not_in(result.impacted_macros,
                                         self._get_nested_macros(i, result))

    def _get_nested_macros(self, line, result):
        macros = []

        for i, _ in enumerate(result.macros_file):
            if (result.lines_start[i] > result.lines_start[line]
               and result.lines_end[i] < result.lines_end[line]):
                macros += self._get_macros_in_line(result.macros_file[i])

        return macros

    def _is_clean(self, macro):
        return ('&&' not in macro and '>' not in macro
                and '<' not in macro and '=' not in macro
                and 'defined"' not in macro and 'ined' not in macro
                and 'this_way"' not in macro and macro.strip() != '1'
                and macro.strip() != '0' and macro.strip() != 'BB_VER')

    def _clean_macro_line(self, macro_line):
        macro = macro_line.replace('!', '').replace('#if', '').replace(
            '#ifdef ', '').replace('#ifndef', '').replace('ndef', '').replace(
            'def', '').replace('ined', ' ').replace('|', ' ').replace(
            '  ', ' ').replace('(', '').replace(')', '')
        macro = re.sub(re.compile("/\*.*?\*/", re.DOTALL), "", macro)
        macro = re.sub(re.compile("//.*?\n"), "", macro)

        return macro

    def _get_macros_in_line(self, macro_line):
        macros_found = []
        macros = self._clean_macro_line(macro_line).split(' ')

        for m in macros:
            m = m.strip()
            if (m and len(m) > 0 and self._is_clean(m)
               and m.strip not in macros_found and not str(m[0]).isdigit()):
                macros_found.append(m.strip())
            else:
                macros = str(m).split('&&')
                for n in macros:
                    n = n.strip()
                    if (n and len(m) > 0 and self._is_clean(n)
                       and n.strip not in macros_found and not str(n[0]).isdigit()):
                        macros_found.append(n.strip())

        return macros_found

    def _get_all_macros(self, result):
        for line in result.macros_file:
            append_if_not_in(result.all_macros, self._get_macros_in_line(line))

    def _verbose(self, result):
        print("Lines with #ifdefs: %r" % list(
            zip(result.macros_file,
                zip(result.lines_start, result.lines_end))))
        print("All macros: %r" % result.all_macros)
        print("Changed lines: %r" % result.changed_lines)
        print("Impacted macros: %r" % result.impacted_macros)