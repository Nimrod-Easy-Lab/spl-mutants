import subprocess

from spl_mutants.products.product_generator import get_output_filename


def get_filename(file):
    return get_output_filename(file)


def diff(command_line):
    output = subprocess.getstatusoutput(' '.join(command_line))

    if output[0] == 0:
        return True, output

    return False, output
