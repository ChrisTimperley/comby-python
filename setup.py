# -*- coding: utf-8 -*-
from glob import glob
from setuptools import setup, find_packages
import re
import os

FILE_MODULE = os.path.join(os.path.dirname(__file__), 'src/comby.py')
with open(FILE_MODULE, 'r') as f:
    VERSION = re.search(r"__version__ = '([\d\.]+)'", f.read()).group(1)

setup(version=VERSION)
