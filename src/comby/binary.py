"""This module provides access to the Comby api."""
from __future__ import annotations

__all__ = ("CombyBinary",)

import json
import os
import shlex
import subprocess
from typing import TYPE_CHECKING, override

import attr
from attrs import field
from loguru import logger
from typeguard import typechecked

from comby.core import ConfigJson, ConfigMatch, Environment, LocationRange, Match
from comby.exceptions import CombyBinaryError
from comby.interface import CombyInterface

if TYPE_CHECKING:
    from typing import Iterator, Sequence


_LINE_SEPARATOR = os.linesep
_LINE_SEPARATOR_LENGTH = len(_LINE_SEPARATOR)


@typechecked
@attr.s(auto_attribs=True, frozen=True, slots=True)
class CombyBinary(CombyInterface):
    """
    Provides an interface to the Comby binary.

    location: The location of the Comby binary that should be used.
    language: The default language that should be assumed when dealing with source text where no
    specific language is specified.

    """

    location: str = field(init=False, default="comby")
    language: str = field(init=False, default=".c")

    @property
    @override
    def version(self: CombyInterface) -> str:
        """
        Retrieve the version number of the Comby binary.

        This method accesses the version information of the Comby binary and returns it as a string.
        If the object is not a CombyBinary instance, it raises a TypeError.


        :returns: The version number of the Comby binary.

        :rtype: str
        :raises TypeError: If the object is not an instance of CombyBinary.

        """
        if not isinstance(self, CombyBinary):
            raise TypeError
        return self.call("-version").strip()

    def call(self: CombyBinary, args: str, text: str | None = None) -> str:
        """
        Call the Comby binary.

        :param args: the arguments that should be supplied to the binary.
        :type args: str
        :param text: (Default value = None) the arguments that should be supplied to the binary.
        :type text: str | None
        :raises CombyBinaryError: if the binary produces a non-zero return code.

        """
        logger.debug(f"calling comby with args: {args}")
        input_ = None
        if text:
            input_ = text.encode("utf8")
            logger.debug(f"supplying input text: {text}")

        cmd_s = f"{self.location} {args}"
        subprocess_result = subprocess.run(
            cmd_s,
            shell=True,
            capture_output=True,
            input=input_,
            check=True,
        )

        err = subprocess_result.stderr.decode("utf8")
        out = subprocess_result.stdout.decode("utf8")
        logger.debug(f"stderr: {err}")
        logger.debug(f"stdout: {out}")

        if subprocess_result.returncode != 0:
            raise CombyBinaryError(code=subprocess_result.returncode, message=err)
        return out

    @override
    def matches(
        self: CombyInterface,
        source: str,
        template: str,
        *,
        language: str | None = None,
    ) -> Iterator[Match]:
        """
        List of matches of a given template within a source text.

        :param source: the source text to search for matches.
        :type source: str
        :param template: the comby template to use to search for matches.
        :type template: str
        :param *:
        :param language: (Default value = None) the language to use for the matcher.
        :type language: str | None
        """
        if not isinstance(self, CombyBinary):
            raise TypeError
        match_log: str = " ".join(
            [
                "finding matches of template",
                template,
                " in source:",
                source,
            ],
        )

        logger.info(match_log)
        if language:
            logger.info(f"using language override: {language}")
        else:
            language = self.language
            logger.info(f"using default language: {language}")

        cmd = (
            "-stdin",
            "-json-lines",
            "-match-only",
            "-matcher",
            shlex.quote(language),
            shlex.quote(template),
            "foo",
        )
        cmd_s: str = " ".join(cmd)

        jsn: ConfigJson | None = json.loads(self.call(cmd_s, text=source) or "null")

        if jsn is not None:
            jsn_matches: list[ConfigMatch] | None = jsn.get("matches")
            if jsn_matches is None:
                raise TypeError
            jsn_match: ConfigMatch
            for jsn_match in jsn_matches:
                matched_raw: str | None = jsn_match.get("matched")
                if matched_raw is None:
                    raise TypeError
                matched: str = matched_raw

                location_raw: dict[str, dict[str, int]] | None = jsn_match.get("range")
                if location_raw is None:
                    raise TypeError
                location: LocationRange = LocationRange.from_dict(location_raw)

                environment_raw: Sequence[
                    dict[str, str | dict[str, dict[str, int]]]
                ] | None = jsn_match.get("environment")
                if environment_raw is None:
                    raise TypeError
                environment: Environment = Environment.from_dict(
                    environment_raw
                )  # Assuming Environment.from_dict exists

                # Create a new dictionary with converted types
                converted_jsn_match: dict[str, str | LocationRange | Environment] = {
                    "matched": matched,
                    "location": location,
                    "environment": environment,
                }

                yield Match.from_dict(converted_jsn_match)

    @override
    def rewrite(
        self: CombyInterface,
        source: str,
        match: str,
        rewrite: str,
        args: dict[str, str] | None = None,
        *,
        diff: bool = False,
        language: str | None = None,
        match_newline_at_toplevel: bool = False,
    ) -> str:
        """
        Rewrite all matches in source with rewrite template.

        :param source: the source text to rewrite.
        :type source: str
        :param match: the comby template to use to search for matches.
        :type match: str
        :param rewrite: the comby template to use to rewrite matches.
        :type rewrite: str
        :param args: (Default value = None)
        :type args: dict[str, str] | None
        :param *:
        :param diff: (Default value = False)
        :type diff: bool
        :param language: (Default value = None) the language to use for the matcher.
        :type language: str | None
        :param match_newline_at_toplevel: (Default value = False) whether to match newline
            at toplevel.
        :type match_newline_at_toplevel: bool
        """
        if not isinstance(self, CombyBinary):
            raise TypeError
        rewrite_log = " ".join(
            [
                "performing rewriting of source",
                source,
                "using match template",
                match,
                "rewrite template",
                rewrite,
                "and arguments",
                f"{args!r}",
            ],
        )
        logger.info(rewrite_log)
        if language:
            logger.info(f"using language override: {language}")
        else:
            language = self.language
            logger.info(f"using default language: {language}")

        if args is None:
            args = {}
        if args:
            raise NotImplementedError

        cmd = ["-stdin", shlex.quote(match), shlex.quote(rewrite)]
        cmd += ["-matcher", shlex.quote(language)]
        cmd += ["-diff" if diff else "-stdout"]
        if match_newline_at_toplevel:
            cmd += ["-match-newline-at-toplevel"]
        cmd_s = " ".join(cmd)

        return self.call(cmd_s, text=source)

    @override
    def substitute(
        self: CombyInterface,
        template: str,
        args: dict[str, str],
        *,
        language: str | None = None,
    ) -> str:
        """
        Substitutes a set of terms into a given template.

        :param template:
        :type template: str
        :param args:
        :type args: dict[str, str]
        :param *:
        :param language: (Default value = None) the language to use for the matcher.
        :type language: str | None
        """
        if not isinstance(self, CombyBinary):
            raise TypeError
        logger.info(f"performing substitution of arguments ({args}) into template ({template})")
        if language:
            logger.info(f"using language override: {language}")
        else:
            language = self.language
            logger.info(f"using default language: {language}")

        substitutions = [
            {"variable": variable, "value": value} for (variable, value) in args.items()
        ]
        encoded_substitutions = shlex.quote(json.dumps(substitutions))
        logger.debug(f"encoded substitutions: {encoded_substitutions}")

        cmd = (
            "IGNORE_MATCHED_TEMPLATE",
            shlex.quote(template),
            "-matcher",
            shlex.quote(language),
            "-substitute-only",
            encoded_substitutions,
        )
        cmd_string = " ".join(cmd)
        result = self.call(cmd_string)

        # remove any trailing line separator
        if result.endswith(_LINE_SEPARATOR):
            result = result[:-_LINE_SEPARATOR_LENGTH]

        return result
