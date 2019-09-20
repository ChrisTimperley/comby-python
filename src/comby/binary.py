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
    language: str
        The default language that should be assumed when dealing with source
        text where no specific language is specified.
    """
    location = attr.ib(type=str, default='comby')
    language = attr.ib(type=str, default='.c')

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
        input_ = None
        if text:
            input_ = text.encode('utf8')
            logger.debug('supplying input text: %s', text)

        cmd_s = '{} {}'.format(self.location, args)
        p = subprocess.run(cmd_s,
                           shell=True,
                           stderr=subprocess.PIPE,
                           stdout=subprocess.PIPE,
                           input=input_)

        if p.returncode != 0:
            raise CombyBinaryError(p.returncode, p.stderr.decode('utf8'))

        out = p.stdout.decode('utf8')
        logger.debug('raw output: %s', out)
        return out

    def matches(self,
                source: str,
                template: str,
                *,
                language: Optional[str] = None
                ) -> Iterator[Match]:
        logger.info("finding matches of template [%s] in source: %s",
                    template, source)
        if language:
            logger.info("using language override: %s", language)
        else:
            language = self.language
            logger.info("using default language: %s", language)

        cmd = ('-stdin', '-json-pretty', '-match-only',
               '-matcher', shlex.quote(language),
               shlex.quote(template), 'foo')
        cmd_s = ' '.join(cmd)

        jsn = json.loads(self.call(cmd_s, text=source))
        jsn = jsn['matches']
        for jsn_match in jsn:
            yield Match.from_dict(jsn_match)

    def rewrite(self,
                source: str,
                match: str,
                rewrite: str,
                args: Optional[Dict[str, str]] = None,
                *,
                language: Optional[str] = None
                ) -> str:
        logger.info("performing rewriting of source (%s) using match template "
                    "(%s), rewrite template (%s) and arguments (%s)",
                    source, match, rewrite, repr(args))
        if language:
            logger.info("using language override: %s", language)
        else:
            language = self.language
            logger.info("using default language: %s", language)

        if args is None:
            args = {}
        if args:
            raise NotImplementedError("args are not currently supported")

        cmd = ['-stdin', shlex.quote(match), shlex.quote(rewrite)]
        cmd += ['-stdout', '-matcher', shlex.quote(language)]
        cmd_s = ' '.join(cmd)

        return self.call(cmd_s, text=source)

    def substitute(self,
                   template: str,
                   args: Dict[str, str],
                   *,
                   language: Optional[str] = None
                   ) -> str:
        raise NotImplementedError
