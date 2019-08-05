# -*- coding: utf-8 -*-
from glob import glob
from setuptools import setup, find_packages
import os

path = os.path.join(os.path.dirname(__file__), 'src/comby/version.py')
with open(path, 'r') as f:
    exec(f.read())

setup(
    name='comby',
    version=__version__,
    description='Lightweight language-independent syntax rewriting.',
    author='Christopher Timperley',
    author_email='christimperley@googlemail.com',
    url='https://github.com/ChrisTimperley/comby-python',
    license='mit',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=3.5',
    install_requires=[
        'requests>=2.0.0',
        'typing>=0.4.1'
    ],
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[
        splitext(basename(path))[0] for path in glob('src/*.py')
    ]
)
