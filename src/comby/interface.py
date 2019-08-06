# -*- coding: utf-8 -*-
"""
This module defines a standard interface for interacting with Comby.
"""
__all__ = ('CombyInterface',)

from typing import Iterator, Dict, Optional
import abc

from .core import Match


class CombyInterface(abc.ABC):
    """Provides a standard interface for interacting with Comby."""
    @abc.abstractmethod
    def matches(self, source: str, template: str) -> Iterator[Match]:
        """Finds all matches of a given template within a source text.

        Parameters:
            source: the source text to be searched.
            template: the template that should be used for matching.

        Returns:
            an iterator over all matches in the text.
        """
        ...

    @abc.abstractmethod
    def substitute(self,
                   template: str,
                   args: Dict[str, str]
                   ) -> str:
        """Substitutes a set of terms into a given template."""
        ...

    @abc.abstractmethod
    def rewrite(self,
                source: str,
                match: str,
                rewrite: str,
                args: Optional[Dict[str, str]] = None
                ) -> str:
        """
        Rewrites all matches of a template in a source text using a rewrite
        template and an optional set of arguments to that rewrite template.
        """
        ...
