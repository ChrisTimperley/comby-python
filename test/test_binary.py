# -*- coding: utf-8 -*-
import logging

import pytest

from comby import CombyBinary


def test_match():
    comby = CombyBinary()
    source = "print('hello world')"
    template = "print(:[1])"
    comby.matches(source, template)


if __name__ == '__main__':
    logging.basicConfig()
    test_match()
