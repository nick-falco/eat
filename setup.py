import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/nick-falco/eat>`_.
"""

version_path = 'eat/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

url = "https://github.com/nick-falco/eat"
setup(
    name='evolution_of_algebraic_terms',
    version=VERSION,
    packages=['eat',
              'eat/beam_algorithm',
              'eat/core',
              'eat/deep_drilling_algorithm',
              'eat/utilities'],
    package_data={'eat': ['VERSION']},
    author="Nicholas Falco, David M. Clark",
    author_email="ncfalco@gmail.com",
    include_package_data=True,
    install_requires=[
        'matplotlib>=3.6,<4',
    ],
    license='Apache License, Version 2.0',
    keywords=("evolutionary-computation genetics ternary-descriminator "
              "idemprimality groupoid machine-learning artifical-intellegence "
              "ai"),
    description=("EAT is software implementation of the algorithms described "
                 "in the paper Evolution of Algebraic Terms 4: Biological "
                 "Beam Algorithms."),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={
        'console_scripts': [
            'eat=eat.runeat:main',
            'eat-tests=eat.runtests:main'
        ]
    }
)
