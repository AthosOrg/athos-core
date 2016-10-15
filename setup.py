#!/usr/bin/env python

from setuptools import setup, find_packages

# get requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='athos-core',
    description = 'Athos project core',
    url = 'https://github.com/AthosOrg/',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'athos-core=athos.cmd:main'
        ]
    },
    install_requires = required,
    package_data = {'athos': ['default.yml']}
)