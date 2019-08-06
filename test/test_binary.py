# -*- coding: utf-8 -*-
import logging

import pytest

from comby import CombyBinary


def test_match():
    comby = CombyBinary()
    source = "print('hello world')"
    template = "print(:[1])"
    matches = list(comby.matches(source, template))
    assert len(matches) == 1
    print(matches[0])


def test_rewrite():
    comby = CombyBinary()
    source = "print('hello world')"
    template = "print(:[1])"
    rewrite = "println(:[1])"
    expected = "println('hello world')"
    actual = comby.rewrite(source, template, rewrite)
    assert actual == expected


if __name__ == '__main__':
    logging.basicConfig()
    test_rewrite()
