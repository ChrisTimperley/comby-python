# -*- coding: utf-8 -*-
"""
This module implements an interface for communicating with Comby over HTTP.
"""
__all__ = ('CombyHTTP',)

from typing import Dict, Iterator, Optional
from urllib.parse import urljoin, urlparse
from contextlib import contextmanager
from timeit import default_timer as timer
import os
import logging
import subprocess
import signal

import requests

from .core import Match
from .interface import CombyInterface
from .exceptions import ConnectionFailure

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


class CombyHTTP(CombyInterface):
    """Provides an interface for communicating with a Comby HTTP server."""
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

    def substitute(self, template: str, args: Dict[str, str]) -> str:
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
