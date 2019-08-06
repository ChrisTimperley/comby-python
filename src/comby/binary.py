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

    def call(self, args: str, text: Optional[str] = None) -> str:
        """Calls the Comby binary.

        Arguments
        ---------
        args: str
            the arguments that should be supplied to the binary.
        text: Optional[str]
            the optional input text that should be supplied to the binary.

        Returns
        -------
        str
            the output of the execution.

        Raises
        ------
        CombyBinaryError
            if the binary produces a non-zero return code.
        """
        logger.debug('calling comby with args: %s', args)
        inp = None
        if text:
            logger.debug('supplying input text: %s', text)
            inp = text.encode('utf8')

        cmd_s = '{} {}'.format(self.location, args)
        p = subprocess.run(cmd_s,
                           shell=True,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           input=inp)

        if p.returncode != 0:
            raise CombyBinaryError(p.returncode, p.stderr.decode('utf8'))

        out = p.stdout.decode('utf8')
        logger.debug('raw output: %s', out)
        return out

    def matches(self, source: str, template: str) -> Iterator[Match]:
        logger.info("finding matches of template [%s] in source: %s",
                    template, source)

        args = ('-stdin', '-json-pretty', '-match-only',
                shlex.quote(template), 'foo')
        args_s = ' '.join(args)

        jsn = json.loads(self.call(args_s, text=source))
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
