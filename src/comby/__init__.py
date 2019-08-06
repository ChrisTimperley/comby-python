# -*- coding: utf-8 -*-
"""
This package provides a set of Python bindings for Comby, a general purpose
tool for matching and rewriting code in arbitrary languages.
"""
import logging

from .core import (Location, LocationRange, BoundTerm, Environment, Match,
                   CombyInterface, CombyHTTP, CombyException)
from .http import CombyHTTP

__version__ = '0.0.1'

logging.getLogger(__name__).setLevel(logging.DEBUG)
