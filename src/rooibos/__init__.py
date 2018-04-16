from typing import Dict, Tuple, Iterator, List
from urllib.parse import urljoin, urlparse

import requests


class LocationRange(object):
    """
    Represents a contiguous range of locations within a given source text as an
    inclusive range of character positions.
    """
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

    def __getitem__(self, term: str) -> BoundTerm:
        """
        Fetches details of a particular term within this environment.

        Parameters:
            term: the name of the term.

        Returns:
            details of the source to which the term was bound.

        Raises:
            KeyError: if no term is found with the given name.
        """
        return self.__bindings[term]


class Match(object):
    """
    Describes a single match of a given template in a source text as a mapping
    of template terms to snippets of source code.
    """
    def __init__(self,
                 environment: Environment,
                 location: LocationRange
                 ) -> None:
        """
        Constructs a new match.

        Parameters:
            environment: an environment that describes the mapping from terms
                in the match template to snippets within the source text.
            location: the location range over which the template was matched.
        """
        self.__environment = environment
        self.__location = location

    def __getitem__(self, term: str) -> BoundTerm:
        """
        Retrieves a bound term from this match.

        Parameters:
            term: the name of the term.

        Returns:
            details of the source code to which the term was bound.

        Raises:
            KeyError: if there is no term with the given name in the match.
        """
        return self.__environment[term]

    @property
    def environment(self) -> Environment:
        """
        The environment that defines the mapping from terms in the match
        template to snippets in the source code.
        """
        return self.__environment

    @property
    def location(self) -> Location:
        """
        The range of locations in the source text over which the template was
        matched.
        """
        return self.__location


class Client(object):
    """
    Provides an interface for communicating with a Rooibos server.
    """
    def __init__(self, base_url: str) -> None:
        """
        Constructs a new client.

        Parameters:
            base_url: the base URL of the Rooibos server.
        """
        self.__base_url = base_url

    @property
    def base_url(self) -> str:
        """
        The base URL of the Rooibos server to which this client is attached.
        """
        return self.__base_url

    def _url(self, path: str) -> str:
        return urljoin(self.__base_url, path)

    def matches(self,
                source: str,
                template: str
                ) -> Iterator[Match]:
        """
        Finds all matches of a given template within a provided body of source
        code.

        Parameters:
            source: the body of source code to be searched.
            template: the template that should be used for matching.

        Returns:
            an iterator over all of the discovered matches within the source.
        """
        path = "matches/{}".format(template)
        url = self._url(path)

        # FIXME
        response = requests.post(url, data=COOL)
        jsn_matches = reversed(response.json())

        while jsn_matches != []:
            jsn_match = jsn_matches.pop()
            location = LocationRange.from_string(jsn_match['location'])
            environment = Environment.from_dict(jsn_match['environment'])
            yield Match(environment, location)

    def rewrite(self,
                source: str,
                match_template: str,
                rewrite_template: str
                ) -> str:
        raise NotImplementedError
