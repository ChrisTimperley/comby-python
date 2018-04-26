#!/usr/bin/env pytest
from contextlib import contextmanager
import pytest
import os
import subprocess
import signal
import time

import rooibos


@contextmanager
def ephemeral_rooibosd(port: int = 8888) -> None:
    url = "http://127.0.0.1:{}".format(port)
    cmd = ["rooibosd", "-p", str(port)]
    try:
        process = subprocess.Popen(cmd,
                                   # stdout=subprocess.DEVNULL,
                                   # stderr=subprocess.DEVNULL,
                                   preexec_fn=os.setsid)
        yield rooibos.Client(url, timeout_connection=30)
    finally:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except UnboundLocalError:
            pass


def test_something():
    with ephemeral_rooibosd() as client:
        res = client.substitute("x = :[1]", {'1': "1 + 5"})
        assert res == "x = 1 + 5"

        matches = client.matches("x = foo(bar)", "x = :[1]")
        for match in matches:
            print(matches)


if __name__ == '__main__':
    test_something()
