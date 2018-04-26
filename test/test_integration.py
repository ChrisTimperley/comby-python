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
        # TODO adding waiting to client constructor
        time.sleep(5)
        yield rooibos.Client(url)
    finally:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except UnboundLocalError:
            pass


def test_something():
    with ephemeral_rooibosd() as client:
        print("nice face")


if __name__ == '__main__':
    test_something()
