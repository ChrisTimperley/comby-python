from typing import Dict, Tuple, Iterator, List, Any
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse
from tempfile import TemporaryFile
from timeit import default_timer as timer
import time
import os
import subprocess
import signal

import requests

from .version import __version__
from .exceptions import *

__all__ = [
    'Location',
    'LocationRange',
    'BoundTerm',
    'Environment',
    'Match',
    'Client',
    'ephemeral_server'
]

class Location(object):
    """
    Represents the location of a single character within a source text by its
    one-indexed line and column numbers.
    """
    @staticmethod
    def from_string(s: str) -> 'Location':
        s_line, _, s_col = s.partition(":")
        line = int(s_line)
        col = int(s_col)
        return Location(line, col)

    def __init__(self, line: int, col: int) -> None:
        assert line > 0, "expected one-indexed line number"
        assert col > 0, "expected one-indexed column number"
        self.__line = line
        self.__col = col

    def __str__(self) -> str:
        """
        Describes this location as a string of the form `line:col`, where
        `line and `col` are one-indexed line and column numbers.
        """
        return "{}:{}".format(self.line, self.col)

    @property
    def line(self) -> int:
        """
        The one-indexed line number for this location.
        """
        return self.__line

    @property
    def col(self) -> int:
        """
        The one-indexed column number for this location.
        """
        return self.__col


class LocationRange(object):
    """
    Represents a contiguous range of locations within a given source text as an
    inclusive range of character positions.
    """
    @staticmethod
    def from_string(s: str) -> 'LocationRange':
        s_start, _, s_end = s.partition("::")
        loc_start = Location.from_string(s_start)
        loc_end = Location.from_string(s_end)
        return LocationRange(loc_start, loc_end)

    def __init__(self, start: Location, stop: Location) -> None:
        """
        Constructs an inclusive location range from a start and stop location.

        Parameters:
            start: the location at which the range begins.
            stop: the location at which the range ends (inclusive).
        """
        self.__start = start
        self.__stop = stop

    def __str__(self) -> str:
        """
        Describes this location range as a string of the form `start::stop`,
        where `start` and `stop` are string-based descriptions of the positions
        of the first and last characters within this source range, respectively.
        """
        return "{}::{}".format(self.start, self.stop)

    @property
    def start(self) -> Location:
        """
        The position at which this range begins.
        """
        return self.__start

    @property
    def stop(self) -> Location:
        """
        The position at which this range ends, inclusive.
        """
        return self.__stop


class BoundTerm(object):
    """
    Represents a binding of a named term to a fragment of source code.
    """
    @staticmethod
    def from_dict(d: dict) -> 'BoundTerm':
        """
        Constructs a bound term from a dictionary-based description.
        """
        return BoundTerm(term=d['term'],
                         location=LocationRange.from_string(d['location']),
                         fragment=d['content'])

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
    @staticmethod
    def from_dict(d: Any) -> 'Environment':
        return Environment([BoundTerm.from_dict(bt) for bt in d])

    def __init__(self,
                 bindings: List[BoundTerm]
                 ) -> None:
        self.__bindings = {b.term: b for b in bindings}

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
    @staticmethod
    def from_dict(d: Any) -> 'Match':
        """
        Constructs a match from a dictionary-based description.
        """
        return Match(environment=d['environment'],
                     location=LocationRange.from_string(d['location']))

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
    def location(self) -> LocationRange:
        """
        The range of locations in the source text over which the template was
        matched.
        """
        return self.__location


class Client(object):
    """
    Provides an interface for communicating with a Rooibos server.
    """
    def __init__(self,
                 base_url: str,
                 timeout: int = 30,
                 timeout_connection: int = 30
                 ) -> None:
        """
        Constructs a new client.

        Parameters:
            base_url: the base URL of the Rooibos server.
            timeout: the maximum number of seconds to wait before terminating
                an unresponsive API request.
            timeout_connection: the maximum number of seconds to wait when
                connecting to the Rooibos server before assuming that a
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
        """
        The base URL of the Rooibos server to which this client is attached.
        """
        return self.__base_url

    def _url(self, path: str) -> str:
        """
        Computes the URL for a resource located at a given path on the server.
        """
        return urljoin(self.__base_url, path)

    def matches(self,
                source: str,
                template: str
                ) -> Iterator[Match]:
        """
        Finds all matches of a given template within a source text.

        Parameters:
            source: the source text to be searched.
            template: the template that should be used for matching.

        Returns:
            an iterator over all matches in the text.
        """
        url = self._url("matches")
        payload = {
            'source': source,
            'template': template
        }
        response = requests.post(url, json=payload)

        # FIXME add error handling
        assert response.status_code == 200

        jsn_matches = list(reversed(response.json()))
        while jsn_matches != []:
            yield Match.from_dict(jsn_matches.pop())

    def substitute(self,
                   template: str,
                   args: Dict[str, str]
                   ) -> str:
        """
        Substitutes a given set of terms into a given template.
        """
        url = self._url("substitute")
        payload = {
            'template': template,
            'arguments': args
        }
        response = requests.post(url, json=payload)
        # FIXME add error handling
        print(response.status_code)
        print(response.text)
        assert response.status_code == 200
        return response.text

    def rewrite(self,
                source: str,
                match: str,
                rewrite: str,
                args: Dict[str, str] = None
                ) -> str:
        """
        Rewrites all matches of a given template in a source text using a
        provided rewrite template and an optional set of arguments to that
        rewrite template.
        """
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
        return response.text


@contextmanager
def ephemeral_server(*,
                     port: int = 6060,
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
    try:
        stdout = None if verbose else subprocess.DEVNULL
        stderr = None if verbose else subprocess.DEVNULL
        proc = subprocess.Popen(cmd,
                                preexec_fn=os.setsid,
                                stdout=stdout,
                                stderr=stderr)
        yield Client(url)
    finally:
        os.killpg(proc.pid, signal.SIGTERM)
