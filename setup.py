#!/usr/bin/env python
from glob import glob
from setuptools import setup, find_packages

setup(
    name='rooibos',
    version='0.0.1',
    description='Lightweight language-independent syntax rewriting.',
    long_description='TBA',
    author='Chris Timperley, Rijnard van Tonder',
    author_email='christimperley@googlemail.com',
    url='https://github.com/squaresLab/rooibos.py',
    license='mit',
    python_requires='>=3.5',
    install_requires=[
        'requests>=2.0.0'
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[
        splitext(basename(path))[0] for path in glob('src/*.py')
    ]
)
