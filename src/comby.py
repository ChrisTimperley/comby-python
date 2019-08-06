# -*- coding: utf-8 -*-
"""
This package provides a set of Python bindings for Comby, a general purpose
tool for matching and rewriting code in arbitrary languages.
"""
__version__ = '0.0.1'
__all__ = (
    'Location',
    'LocationRange',
    'BoundTerm',
    'Environment',
    'Match',
    'Client',
    'CombyException',
    'ConnectionFailure',
    'ephemeral_server'
)

from typing import Dict, Tuple, Iterator, List, Any, Optional, Mapping
from urllib.parse import urljoin, urlparse
from timeit import default_timer as timer
from contextlib import contextmanager
import time
import os
import subprocess
import signal
import logging

import attr
import requests

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


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


class Client:
    """Provides an interface for communicating with a Comby server."""
    def __init__(self,
                 base_url: str,
                 timeout: int = 30,
                 timeout_connection: int = 30
                 ) -> None:
        """Constructs a new client.

        Parameters:
            base_url: the base URL of the Comby server.
            timeout: the maximum number of seconds to wait before terminating
                an unresponsive API request.
            timeout_connection: the maximum number of seconds to wait when
                connecting to the Comby server before assuming that a
                connection failure has occurred.

        Raises:
            ConnectionFailure: if the client failed to connect to the server
                within the connection timeout period.
        """
        self.__base_url = base_url
        self.__timeout = timeout

        # attempt to establish a connection
        url = self._url("status")
        time_left = float(timeout_connection)
        time_started = timer()
        connected = False
        while time_left > 0.0 and not connected:
            try:
                r = requests.get(url, timeout=time_left)
                connected = r.status_code == 204
            except requests.exceptions.ConnectionError:
                time.sleep(1.0)
            except requests.exceptions.Timeout:
                raise ConnectionFailure
            time.sleep(0.05)
            time_left -= timer() - time_started
        if not connected:
            raise ConnectionFailure

    @property
    def base_url(self) -> str:
        """The base URL of the server to which this client is attached."""
        return self.__base_url

    def _url(self, path: str) -> str:
        """Computes the URL for a resource on the server."""
        return urljoin(self.__base_url, path)

    def matches(self, source: str, template: str) -> Iterator[Match]:
        """Finds all matches of a given template within a source text.

        Parameters:
            source: the source text to be searched.
            template: the template that should be used for matching.

        Returns:
            an iterator over all matches in the text.
        """
        logger.info("finding matches of template [%s] in source: %s",
                    template, source)
        url = self._url("matches")
        payload = {
            'source': source,
            'template': template
        }
        response = requests.post(url, json=payload)

        # FIXME add error handling
        assert response.status_code == 200

        jsn_matches = list(reversed(response.json()))
        num_matches = len(jsn_matches)
        logger.info("found %d matches of template [%s] in source: %s",
                    num_matches, template, source)
        i = 0
        while jsn_matches != []:
            i += 1
            match = Match.from_dict(jsn_matches.pop())
            logger.info("* match #%d: %s", i, repr(match))
            yield match

    def substitute(self,
                   template: str,
                   args: Dict[str, str]
                   ) -> str:
        """Substitutes a given set of terms into a given template."""
        logger.info("substituting arguments (%s) into template (%s)",
                    repr(args), template)
        url = self._url("substitute")
        payload = {
            'template': template,
            'arguments': args
        }
        response = requests.post(url, json=payload)
        # FIXME add error handling
        assert response.status_code == 200
        logger.info("substituted arguments (%s) into template (%s): %s",
                    repr(args), template, response.text)
        return response.text

    def rewrite(self,
                source: str,
                match: str,
                rewrite: str,
                args: Optional[Dict[str, str]] = None
                ) -> str:
        """
        Rewrites all matches of a given template in a source text using a
        provided rewrite template and an optional set of arguments to that
        rewrite template.
        """
        logger.info("performing rewriting of source (%s) using match template "
                    "(%s), rewrite template (%s) and arguments (%s)",
                    source, match, rewrite, repr(args))
        if args is None:
            args = {}

        url = self._url("rewrite")
        payload = {
            'source': source,
            'match': match,
            'rewrite': rewrite,
            'arguments': args
        }
        response = requests.post(url, json=payload)
        # FIXME add error handling
        assert response.status_code == 200
        logger.info("performed source code rewrite:\n%s", response.text)
        return response.text


@contextmanager
def ephemeral_server(port: int = 8888,
                     verbose: bool = False
                     ) -> Iterator[Client]:
    """
    Launches an ephemeral server instance that will be immediately
    close when no longer in context.

    Parameters:
        port: the port that the server should run on.
        verbose: if set to True, the server will print its output to the
            stdout, otherwise it will remain silent.

    Returns:
        a client for communicating with the server.
    """
    url = "http://127.0.0.1:{}".format(port)
    cmd = ["rooibosd", "-p", str(port)]
    proc = None
    try:
        stdout = None if verbose else subprocess.DEVNULL
        stderr = None if verbose else subprocess.DEVNULL
        proc = subprocess.Popen(cmd,
                                preexec_fn=os.setsid,
                                stdout=stdout,
                                stderr=stderr)
        yield Client(url)
    finally:
        if proc:
            os.killpg(proc.pid, signal.SIGTERM)
