#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from glob import glob
from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['spacy>=2.0']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest']

setup(
    author="LINHD POSTDATA Project",
    author_email='info@linhd.uned.es',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="""SpaCy support to split affixes for Freeling-like affixes """
                """rules and dictionaries""",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme + '\n\n' + history,
    url='https://github.com/linhd-postdata/spacy-affixes',
    version='0.1.1',
    include_package_data=True,
    keywords='spacy_affixes',
    name='spacy_affixes',

    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],

    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    zip_safe=False,
)
