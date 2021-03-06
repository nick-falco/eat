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
    name='EAT: Evolution of Algebraic Terms',
    version=VERSION,
    packages=['eat'],
    author="Nicholas Falco, David M. Clark",
    author_email="ncfalco@gmail.com",
    include_package_data=True,
    install_requires=[
    ],
    license='Apache License, Version 2.0',
    description=('EAT is software implementation of the algorithms described '
                 'in papers Evolution of Algebraic Terms (EAT), published in '
                 'the International Journal of Algebra and Computation.'),
    long_description=README,
    url=url,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={
        'console_scripts': [
            'eat=runeat:main'
        ]
    }
)
