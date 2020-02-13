# -*- coding: utf-8 -*-
"""
This module implements an binary-based interface for communicating with Comby.
"""
__all__ = ('CombyBinary',)

from typing import Iterator, Optional, Dict
import json
import logging
import os
import subprocess
import shlex

from .core import Match
from .exceptions import CombyBinaryError
from .interface import CombyInterface

import attr

_LINE_SEPARATOR = os.linesep
_LINE_SEPARATOR_LENGTH = len(_LINE_SEPARATOR)

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


@attr.s(frozen=True, slots=True)
class CombyBinary(CombyInterface):
    """Provides an interface to the Comby binary.

    Attributes
    ----------
    location: str
        The location of the Comby binary that should be used.
    language: str
        The default language that should be assumed when dealing with source
        text where no specific language is specified.
    version: str
        The version of Comby that is used by this binary.
    """
    location = attr.ib(type=str, default='comby')
    language = attr.ib(type=str, default='.c')

    @property
    def version(self) -> str:
        return self.call('-version').strip()

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

        cmd = ('-stdin', '-json-lines', '-match-only',
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
                diff: bool = False,
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
        cmd += ['-matcher', shlex.quote(language)]
        cmd += ['-diff' if diff else '-stdout']
        cmd_s = ' '.join(cmd)

        return self.call(cmd_s, text=source)

    def substitute(self,
                   template: str,
                   args: Dict[str, str],
                   *,
                   language: Optional[str] = None
                   ) -> str:
        logger.info(f"performing substitution of arguments ({args}) "
                    f"into template ({template})")
        if language:
            logger.info("using language override: %s", language)
        else:
            language = self.language
            logger.info("using default language: %s", language)

        substitutions = [{'variable': variable, 'value': value}
                         for (variable, value) in args.items()]
        encoded_substitutions = shlex.quote(json.dumps(substitutions))
        logger.debug(f"encoded substitutions: {encoded_substitutions}")

        cmd = ('IGNORE_MATCHED_TEMPLATE', shlex.quote(template),
               '-matcher', shlex.quote(language),
               '-substitute-only', encoded_substitutions)
        cmd_string = ' '.join(cmd)
        result = self.call(cmd_string)

        # remove any trailing line separator
        if result.endswith(_LINE_SEPARATOR):
            result = result[:-_LINE_SEPARATOR_LENGTH]

        return result
