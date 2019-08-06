# -*- coding: utf-8 -*-
"""
This module implements an binary-based interface for communicating with Comby.
"""
__all__ = ('CombyBinary',)

from typing import Iterator, Optional, Dict
import logging
import subprocess
import shlex
import json

from .interface import CombyInterface
from .core import Match
from .exceptions import CombyBinaryError

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
        cmd_s = ' '.join(cmd)

        logger.debug('calling comby: %s', cmd_s)
        p = subprocess.run(cmd_s,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           shell=True,
                           input=source.encode('utf8'))
        out = p.stdout.decode('utf8')
        if p.returncode != 0:
            raise CombyBinaryError(p.returncode, p.stderr.decode('utf8'))

        jsn = json.loads(out)
        print(jsn)

    def rewrite(self,
                source: str,
                match: str,
                rewrite: str,
                args: Optional[Dict[str, str]] = None
                ) -> str:
        raise NotImplementedError

    def substitute(self, template: str, args: Dict[str, str]) -> str:
        raise NotImplementedError
