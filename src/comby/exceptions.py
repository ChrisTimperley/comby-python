"""This module provides definitions for the exceptions raised by Comby."""
import attr

__all__ = ["CombyExceptionError", "ConnectionFailureError"]


class CombyExceptionError(Exception):
    """Base class used by all Comby exceptions."""


class ConnectionFailureError(CombyExceptionError):
    """
    The client failed to establish a connection to the server.

    The client failed to establish a connection to the server within the allotted
    connection timeout window.


    :raises ConnectionFailureError: always

    """


@attr.s(auto_attribs=True)
class CombyBinaryError(CombyExceptionError):
    """An error was produced by the Comby binary."""

    code: int
    message: str
