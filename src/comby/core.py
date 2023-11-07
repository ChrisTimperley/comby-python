"""This module provides the core data structures."""
from __future__ import annotations

__all__ = ("Location", "LocationRange", "BoundTerm", "Environment", "Match")

from typing import Iterator, Mapping, Sequence, TypedDict, override

import attr
from typeguard import typechecked

# Create a new Location object.


@typechecked
@attr.s(auto_attribs=True, frozen=True, slots=True)
class Location:
    """
    Represent a location in source code, with line, column, and byte offset.

    This is an immutable data class.

    """

    line: int
    col: int
    offset: int

    @staticmethod
    def from_dict(location_dict: dict[str, int]) -> Location:
        """
        Create a Location object from a dictionary.

        :param location_dict: A dictionary containing the keys "line", "column", and "offset".
        :type location_dict: dict[str, int]
        :returns: A Location object.
        :rtype: Location
        """
        return Location(
            line=location_dict["line"],
            col=location_dict["column"],
            offset=location_dict["offset"],
        )


@typechecked
@attr.s(auto_attribs=True, frozen=True, slots=True, str=False)
class LocationRange:
    """Represent a range of locations in a source code."""

    start: Location
    stop: Location

    @staticmethod
    def from_dict(location_range_dict: dict[str, dict[str, int]]) -> LocationRange:
        """
        Create a LocationRange object from a dictionary representation.

        :param location_range_dict:
        :type location_range_dict: dict[str, dict[str, int]]
        :returns: The created LocationRange object.
        :rtype: LocationRange
        """
        return LocationRange(
            start=Location.from_dict(location_range_dict["start"]),
            stop=Location.from_dict(
                location_range_dict["end"],
            ),
        )


@typechecked
@attr.s(auto_attribs=True, frozen=True, slots=True)
class BoundTerm:
    """Represent a binding of a named term to a fragment of source code."""

    term: str
    location: LocationRange
    fragment: str

    @staticmethod
    def from_dict(bound_term_dict: dict[str, str | dict[str, dict[str, int]]]) -> BoundTerm:
        """
        Create a BoundTerm object from a dictionary representation.

        :param bound_term_dict:
        :type bound_term_dict: dict[str, str | dict[str, dict[str, int]]]
        """
        term = bound_term_dict["variable"]
        location = bound_term_dict["range"]
        fragment = bound_term_dict["value"]

        if not isinstance(term, str):
            raise TypeError

        if not isinstance(location, dict):
            raise TypeError

        if not isinstance(fragment, str):
            raise TypeError

        return BoundTerm(
            term=term,
            location=LocationRange.from_dict(location),
            fragment=fragment,
        )


@typechecked
class Environment(Mapping[str, BoundTerm]):
    """
    The `Environment` class represents a mapping of string keys to `BoundTerm` values.

    It provides methods to access and manipulate the mappings.

    """

    def __init__(self: Environment, bindings: Sequence[BoundTerm]) -> None:
        """
        Initialize an instance of the Environment class.

        :param bindings:
        :type bindings: Sequence[BoundTerm]
        """
        super().__init__()
        self.__bindings = {b.term: b for b in bindings}

    @staticmethod
    def from_dict(ts: Sequence[dict[str, str | dict[str, dict[str, int]]]]) -> Environment:
        """
        Create an Environment object from a list of dictionaries.

        :param ts: A list of dictionaries representing the bindings.
        :type ts: Sequence[dict[str, str | dict[str, dict[str, int]]]]
        :returns: An Environment object.
        :rtype: Environment
        """
        return Environment(
            bindings=[BoundTerm.from_dict(bt) for bt in ts],
        )

    @override
    def __repr__(self: Environment) -> str:
        """
        Return a string representation of the Environment object.

        The string representation is a list of the bindings in the environment


        :returns: A string representation of the Environment object.

        :rtype: str
        """
        environment_str = "".join(
            [
                "comby.Environment([])",
            ],
        )
        return environment_str.format(
            ", ".join([repr(self[t]) for t in self]),
        )

    @override
    def __len__(self: Environment) -> int:
        """
        Return the number of bindings in the environment.

        Length of the environment.


        :returns: The number of bindings in the environment.

        :rtype: int
        """
        return len(self.__bindings)

    @override
    def __iter__(self: Environment) -> Iterator[str]:
        """
        Return an iterator over the term names in the environment.

        The iterator yields the names of the bindings in the environment.


        :returns: An iterator over the term names in the environment.

        :rtype: Iterator[str]
        """
        return self.__bindings.keys().__iter__()

    @override
    def __getitem__(self: Environment, term: str) -> BoundTerm:
        """
        Return the `BoundTerm` value associated with the given term name.

        :param term:
        :type term: str
        """
        return self.__bindings[term]


@typechecked
@attr.s(auto_attribs=True, slots=True, frozen=True)
class Match(Mapping[str, BoundTerm]):
    """
    The `Match` class represents a mapping of string keys to `BoundTerm` values.

    It provides methods to access and manipulate the mappings.

    """

    matched: str
    location: LocationRange
    environment: Environment

    @staticmethod
    def from_dict(match_dict: dict[str, str | LocationRange | Environment]) -> Match:
        """
        Create a `Match` object from a dictionary representation.

        :param match_dict: The dictionary representation of the `Match` object.
        :type match_dict: dict[str, str | LocationRange | Environment]
        :returns: The created `Match` object.
        :rtype: Match
        :raises TypeError: If the types of the values in the dictionary are not valid.

        """
        matched = match_dict["matched"]
        location = match_dict["location"]
        environment = match_dict["environment"]

        if not isinstance(matched, str):
            raise TypeError

        if not isinstance(location, LocationRange):
            raise TypeError

        if not isinstance(environment, Environment):
            raise TypeError

        return Match(
            matched=matched,
            location=location,
            environment=environment,
        )

    @override
    def __len__(self: Match) -> int:
        """
        Return the number of bindings in the environment.

        The number of bindings in the environment.


        :returns: The number of bindings in the environment.

        :rtype: int
        """
        return len(self.environment)

    @override
    def __iter__(self: Match) -> Iterator[str]:
        """
        Return an iterator over the term names in the environment.

        The iterator yields the names of the bindings in the environment.


        :returns: An iterator over the term names in the environment.

        :rtype: Iterator[str]
        """
        yield from self.environment

    @override
    def __getitem__(self: Match, term: str) -> BoundTerm:
        """
        Return the `BoundTerm` value associated with the given term name from the environment.

        :param term: The term name.
        :type term: str
        :returns: The `BoundTerm` value associated with the term name.
        :rtype: BoundTerm
        """
        return self.environment[term]


@typechecked
class ConfigMatch(TypedDict):
    """Config match."""

    matched: str
    range: dict[str, dict[str, int]]
    environment: Sequence[dict[str, str | dict[str, dict[str, int]]]]


@typechecked
class ConfigJson(TypedDict):
    """Config json."""

    matches: list[ConfigMatch]
    uri: None


@typechecked
class ConfigLocation(TypedDict):
    """Config location."""

    start: dict[str, int]
    end: dict[str, int]
