from typing import Dict, Tuple, Iterator, List

import requests


class LocationRange(object):
    pass


class BoundTerm(object):
    """
    Represents a binding of a named term to a fragment of source code.
    """
    def __init__(self,
                 term: str,
                 location: LocationRange,
                 fragment: str
                 ) -> None:
        """
        Constructs a new bound term.

        Parameters:
            term: the name of the term.
            location: the location range at which the term was bound.
            fragment: the source code to which the term was bound.
        """
        self.__term = term
        self.__location = location
        self.__fragment = fragment

    @property
    def term(self) -> str:
        """
        The name of the term.
        """
        return self.__term

    @property
    def location(self) -> LocationRange:
        """
        The location range covered by this term.
        """
        return self.__location

    @property
    def fragment(self) -> str:
        """
        The source code fragment to which this term is bound, given as a
        string.
        """
        return self.__fragment


class Environment(object):
    def __init__(self,
                 bindings: Dict[str, BoundTerm]
                 ) -> None:
        self.__bindings = bindings

    def __iter__(self) -> Iterator[str]:
        """
        Returns an iterator over the names of the terms contained within
        this environment.
        """
        return self.__bindings.keys().__iter__()


class Match(object):
    pass

class Client(object):
    def __init__(self, base_url: str) -> None:
        self.__base_url = base_url

    @property
    def base_url(self) -> str:
        """
        The base URL of the Rooibos server to which this client is attached.
        """
        return self.__base_url

    def matches(self,
                source: str,
                match_template: str
                ) -> Iterator[Match]:
        """
        Finds all matches of a given template within a provided body of source
        code.

        Parameters:
            source: the body of source code to be searched.
            match_template: the template that should be used for matching.

        Returns:
            an iterator over all of the discovered matches within the source.
        """
        raise NotImplementedError

    def rewrite(self,
                source: str,
                match_template: str,
                rewrite_template: str
                ) -> str:
        raise NotImplementedError
