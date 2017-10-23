import os
from tinydb import TinyDB


class Config:

    def __init__(self):
        self.state_file = '_db.json'
        self.source_dir = None
        self.source_file = None
        self.include_dirs = None
        self.output_dir = None
        self.mutants_dir = None


class State:

    def __init__(self, config):
        self.db = TinyDB(os.path.join(config.output_dir, config.state_file))
        self.db.insert({
            'type': 'config',
            'source_dir': config.source_dir,
            'source_file': config.source_file,
            'include_dirs': config.include_dirs,
            'output_dir': config.output_dir,
            'mutants_dir': config.mutants_dir,
            'product_versions': 0,
            'products_dir': None,
            'products': 0,
            'products_impacted': 0,
            'macros': []
        })

    def _state(self):
        return self.db.all()[0]

    @property
    def source_dir(self):
        return self._state().get('source_dir')

    @property
    def source_file(self):
        return self._state().get('source_file')

    @property
    def include_dirs(self):
        return self._state().get('include_dirs')

    @property
    def output_dir(self):
        return self._state().get('output_dir')

    @property
    def mutants_dir(self):
        return self._state().get('mutants_dir')

    @property
    def products_dir(self):
        return self._state().get('products_dir')
