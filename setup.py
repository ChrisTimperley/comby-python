from glob import glob
from setuptools import setup, find_packages
import os

path = os.path.join(os.path.dirname(__file__), 'src/rooibos/version.py')
with open(path, 'r') as f:
    exec(f.read())

setup(
    name='rooibos',
    version=__version__,
    description='Lightweight language-independent syntax rewriting.',
    author='Chris Timperley, Rijnard van Tonder',
    author_email='christimperley@googlemail.com',
    url='https://github.com/squaresLab/rooibos.py',
    license='mit',
    classifiers=[
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    python_requires='>=2.7',
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
