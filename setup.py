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
