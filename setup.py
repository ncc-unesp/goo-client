# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

with open('README.rst') as readme:
    long_description = readme.read()

with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n') if (line and not
                                                     line.startswith('--'))
    ]

setup(
    name='goo-client',
    version='0.1.0',
    author='Beraldo Leal',
    author_email='beraldo@ncc.unesp.br',
    packages=find_packages(exclude=['test', 'bin']),
    url='http://goo.ncc.unesp.br/',
    license='LICENSE',
    description='Goo command line client.',
    install_requires=install_requires,
    scripts=[
        'scripts/goo-client',
    ],
)
