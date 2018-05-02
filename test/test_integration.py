#!/usr/bin/env pytest
from typing import List, Set, Dict, Tuple, FrozenSet
from contextlib import contextmanager
import pytest
import os
import subprocess
import signal
import time
import logging

import rooibos


def test_something():
    logging.getLogger('rooibos').addHandler(logging.StreamHandler())
    with rooibos.ephemeral_server() as client:
        res = client.substitute("x = :[1]", {'1': "1 + 5"})
        assert res == "x = 1 + 5"

        def env_to_pair_set(env: rooibos.Environment) -> FrozenSet[Tuple[str, str]]:
            return frozenset((name, env[name].fragment) for name in env)

        def dict_to_pair_set(d: Dict[str, str]) -> FrozenSet[Tuple[str, str]]:
            return frozenset((k, v) for k, v in d.items())

        def check_matches(src: str, tpl: str, expected: List[Dict[str, str]]) -> None:
            matches = list(client.matches(src, tpl))
            actual = frozenset(env_to_pair_set(m.environment) for m in matches)
            assert actual == frozenset(dict_to_pair_set(m) for m in expected)

        check_matches("x = foo(bar)", "x = :[1]", [{'1': "foo(bar)"}])


if __name__ == '__main__':
    test_something()
