# -*- coding: utf-8 -*-
import setuptools
import re
import os

path = os.path.join(os.path.dirname(__file__), 'src/comby/__init__.py')
with open(path, 'r') as f:
    VERSION=re.search(r"__version__ = '([\d\.]+)'", f.read()).group(1)

setuptools.setup(version=VERSION)
