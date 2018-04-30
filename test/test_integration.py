#!/usr/bin/env pytest
from contextlib import contextmanager
import pytest
import os
import subprocess
import signal
import time

import rooibos


def test_something():
    with rooibos.ephemeral_server() as client:
        res = client.substitute("x = :[1]", {'1': "1 + 5"})
        assert res == "x = 1 + 5"

        matches = client.matches("x = foo(bar)", "x = :[1]")
        for match in matches:
            print(matches)


if __name__ == '__main__':
    test_something()
