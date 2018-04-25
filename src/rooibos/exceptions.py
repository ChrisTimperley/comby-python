__all__ = ['RooibosException', 'ConnectionFailure']


class RooibosException(Exception):
    """
    Base class used by all Rooibos exceptions.
    """


class ConnectionFailure(RooibosException):
    """
    The client failed to establish a connection to the server within the
    allotted connection timeout window.
    """
