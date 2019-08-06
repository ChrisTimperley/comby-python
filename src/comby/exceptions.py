# -*- coding: utf-8 -*-
"""
This module provides definitions for the exceptions raised by Comby.
"""


class CombyException(Exception):
    """Base class used by all Comby exceptions."""


class ConnectionFailure(CombyException):
    """
    The client failed to establish a connection to the server within the
    allotted connection timeout window.
    """
