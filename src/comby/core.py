# -*- coding: utf-8 -*-
"""
This module defines several common data structures for describing code
transformations, source locations, environments, matches, and templates.
Additionally, this module defines a common interface for interacting with
Comby, and implements a number of exceptions.
"""
__all__ = (
    'Location',
    'LocationRange',
    'BoundTerm',
    'Environment',
    'Match',
    'CombyInterface',
    'CombyException',
    'ConnectionFailure'
)

from typing import Dict, Tuple, Iterator, List, Any, Optional, Mapping
import abc

import attr


class CombyException(Exception):
    """Base class used by all Comby exceptions."""


class ConnectionFailure(CombyException):
    """
    The client failed to establish a connection to the server within the
    allotted connection timeout window.
    """


@attr.s(frozen=True, slots=True, str=False)
class Location:
    """
    Represents the location of a single character within a source text by its
    zero-indexed line and column numbers.

    Attributes
    ----------
    line: int
        Zero-indexed line number.
    col: int
        Zero-indexed column number.
    """
    line = attr.ib(type=int)
    col = attr.ib(type=int)

    @staticmethod
    def from_string(s: str) -> 'Location':
        s_line, _, s_col = s.partition(':')
        line = int(s_line)
        col = int(s_col)
        return Location(line, col)

    def __str__(self) -> str:
        """
        Describes this location as a string of the form `line:col`, where
        `line and `col` are one-indexed line and column numbers.
        """
        return "{}:{}".format(self.line, self.col)


@attr.s(frozen=True, slots=True, str=False)
class LocationRange:
    """
    Represents a contiguous range of locations within a given source text as a
    (non-inclusive) range of character positions.

    Attributes
    ----------
    start: Location
        The start of the range.
    stop: Location
        The (non-inclusive) end of the range.
    """
    start = attr.ib(type=Location)
    stop = attr.ib(type=Location)

    @staticmethod
    def from_string(s: str) -> 'LocationRange':
        s_start, _, s_end = s.partition("::")
        loc_start = Location.from_string(s_start)
        loc_end = Location.from_string(s_end)
        return LocationRange(loc_start, loc_end)

    def __str__(self) -> str:
        """
        Describes this location range as a string of the form `start::stop`,
        where `start` and `stop` are string-based descriptions of the positions
        of the first and last characters within this source range,
        respectively.
        """
        return "{}::{}".format(self.start, self.stop)


@attr.s(frozen=True, slots=True)
class BoundTerm:
    """Represents a binding of a named term to a fragment of source code.

    Attributes
    ----------
    term: str
        The name of the term.
    location: LocationRange
        The location range to which the term is bound.
    fragment: str
        The source code to which the term is bound.
    """
    term = attr.ib(type=str)
    location = attr.ib(type=LocationRange)
    fragment = attr.ib(type=str)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'BoundTerm':
        """Constructs a bound term from a dictionary-based description."""
        return BoundTerm(term=d['term'],
                         location=LocationRange.from_string(d['location']),
                         fragment=d['content'])


class Environment(Mapping[str, BoundTerm]):
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Environment':
        return Environment([BoundTerm.from_dict(bt) for bt in d.values()])

    def __init__(self, bindings: List[BoundTerm]) -> None:
        self.__bindings = {b.term: b for b in bindings}

    def __repr__(self) -> str:
        s = "comby.Environment([{}])"
        return s.format(', '.join([repr(self[t]) for t in self]))

    def __len__(self) -> int:
        """Returns the number of bindings in this environment."""
        return len(self.__bindings)

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the term names in this environment."""
        return self.__bindings.keys().__iter__()

    def __getitem__(self, term: str) -> BoundTerm:
        """Fetches details of a particular term within this environment.

        Parameters:
            term: the name of the term.

        Returns:
            details of the source to which the term was bound.

        Raises:
            KeyError: if no term is found with the given name.
        """
        return self.__bindings[term]


@attr.s(slots=True)
class Match(Mapping[str, BoundTerm]):
    """
    Describes a single match of a given template in a source text as a mapping
    of template terms to snippets of source code.
    """
    environment = attr.ib(type=Environment)
    location = attr.ib(type=LocationRange)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'Match':
        """Constructs a match from a dictionary-based description."""
        return Match(Environment.from_dict(d['environment']),
                     LocationRange.from_string(d['location']))

    def __len__(self) -> int:
        """Returns the number of bindings in the environment."""
        return len(self.environment)

    def __iter__(self) -> Iterator[str]:
        """Returns an iterator over the term names in the environment."""
        yield from self.environment

    def __getitem__(self, term: str) -> BoundTerm:
        return self.environment[term]


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
