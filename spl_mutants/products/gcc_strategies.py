import os
import subprocess
import shutil


class GCCConfig:

    def __init__(self):

        self.params = []
        self.input_file = None
        self.output_file = None
        self.source_file = None


class Executor:

    def __init__(self, config, strategy):
        self.config = config
        self.strategy = strategy

    def run(self, source_file=None, log=False):

        if not source_file:
            source_file = self.config.source_file

        command = self.strategy(config=self.config)

        if source_file is not None and source_file != self.config.input_file:
            os.rename(source_file, source_file + '_ori')
            shutil.copy2(os.path.abspath(self.config.input_file), source_file)
            command[-3] = source_file

        if log:
            subprocess.call(command, shell=False)
            self._run_preprocessor_only(source_file)
        else:
            subprocess.call(command, shell=False, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)

        if source_file is not None and source_file != self.config.input_file:
            os.remove(source_file)
            os.rename(source_file + '_ori', source_file)

    def _run_preprocessor_only(self, source_file=None):
        command = gcc_to_log(config=self.config)

        if source_file:
            command[-3] = source_file

        subprocess.call(command, shell=False, stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL)


def gcc_to_tce(config):
    params = ['-c', '-Wfatal-errors', '-Werror=implicit', '-O3'] + config.params
    return _gcc(config=config, params=params)


def gcc_to_log(config):
    params = ['-E', '-P', '-O3'] + config.params
    to_log = _gcc(config=config, params=params)
    to_log[-1] = to_log[-1] + '.c'
    return to_log


def _gcc(config, params):
    return ['gcc'] + params + [config.input_file, '-o', config.output_file]