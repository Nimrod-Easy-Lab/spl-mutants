from setuptools import setup, find_packages
from pip.req import parse_requirements

from spl_mutants.version import __version__


install_reqs = parse_requirements('requirements.txt', session=False)
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="spl-mutants",
    version=__version__,
    packages=find_packages(),

    author="Marcio Augusto Guimarães",
    author_email="masg@ic.ufal.br",

    install_requires=reqs,
    entry_points={
        'console_scripts':  [
            'spl-mutants = spl_mutants.__main__:main'
        ]
    }
)
