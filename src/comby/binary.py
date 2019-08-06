# -*- coding: utf-8 -*-
"""
This module implements an binary-based interface for communicating with Comby.
"""
__all__ = ('CombyBinary',)

from typing import Iterator, Optional, Dict
import logging
import subprocess

from .interface import CombyInterface
from .core import Match

import attr

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True)
class CombyBinary(CombyInterface):
    """Provides an interface to the Comby binary.
    Attributes
    ----------
    location: str
        The location of the Comby binary that should be used.
    """
    location = attr.ib(type=str, default='comby')

    def matches(self, source: str, template: str) -> Iterator[Match]:
        logger.info("finding matches of template [%s] in source: %s",
                    template, source)

        cmd = (self.location, '-stdin', '-json-pretty', '-match-only',
               shlex.quote(template), 'foo')

        # FIXME avoid using shell
        p = subprocess.run(c, stdout=subprocess.PIPE, shell=True,
                           input=source.encode('utf8'))
        assert p.returncode == 0
        jsn = json.loads(p.stdout.decode('utf8'))
        print(jsn)
