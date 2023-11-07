"""
Python bindings for Comby.

This package provides a set of Python bindings for Comby, a general purpose tool for
matching and rewriting code in arbitrary languages.

"""
from loguru import logger as _logger

from comby import exceptions
from comby.binary import CombyBinary
from comby.core import BoundTerm, Environment, Location, LocationRange, Match

Comby = CombyBinary

__version__ = "0.0.2"

_logger.disable("comby")

__all__ = [
    "exceptions",
    "Location",
    "LocationRange",
    "BoundTerm",
    "Environment",
    "Match",
    "CombyBinary",
]
