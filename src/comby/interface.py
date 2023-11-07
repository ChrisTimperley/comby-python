"""
This module defines a standard interface for interacting with Comby.
"""
from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Iterator

from typeguard import typechecked

__all__ = ("CombyInterface",)


if TYPE_CHECKING:
    from comby.core import Match


@typechecked
class CombyInterface(abc.ABC):
    """Provides a standard interface for interacting with Comby."""

    @property
    @abc.abstractmethod
    def version(self: CombyInterface) -> str:
        """
        Retrieve the version number of the Comby binary.

        This method accesses the version information of the Comby binary and returns it as a string.
        If the object is not a CombyBinary instance, it raises a TypeError.


        :returns: The version number of the Comby binary.

        :rtype: str
        :raises TypeError: If the object is not an instance of CombyBinary.

        """
        ...

    @abc.abstractmethod
    def matches(
        self: CombyInterface,
        source: str,
        template: str,
        *,
        language: str | None = None,
    ) -> Iterator[Match]:
        """
        Finds all matches of a given template within a source text.

        :param source: The source text to be searched.
        :type source: str
        :param template: The template that should be used for matching.
        :type template: str
        :param *:
        :param language: Specifies the language of the source text.
            If no language is specified, then the default language associated with this
            interface will be used.
        :type language: str | None
        :returns: An iterator over all matches of the given template within
        :rtype: Iterator[Match]
        :raises None:

        """
        ...

    @abc.abstractmethod
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
        :param language: (Default value = None)
        :type language: str | None
        :raises None:

        """
        ...

    @abc.abstractmethod
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

        Rewrites all matches of a template in a source text using a rewrite template and
        an optional set of arguments to that rewrite template.

        :param source:
        :type source: str
        :param match:
        :type match: str
        :param rewrite:
        :type rewrite: str
        :param args: (Default value = None)
        :type args: dict[str, str] | None
        :param *:
        :param diff: (Default value = False)
        :type diff: bool
        :param language: (Default value = None)
        :type language: str | None
        :param match_newline_at_toplevel: (Default value = False)
        :type match_newline_at_toplevel: bool
        :raises None:

        """
        ...
