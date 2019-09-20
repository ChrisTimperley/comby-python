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

    source = """
    switch (name) {
        case "WALL-E":
            System.out.println("Hey! Stop that droid!");
            break;
        default:
            System.out.println("These aren't the droids we're looking for...");
    }
    """.strip()
    template = 'case "WALL-E"'
    rewrite = 'case "C3PO"'
    expected = """
    switch (name) {
        case "C3PO":
            System.out.println("Hey! Stop that droid!");
            break;
        default:
            System.out.println("These aren't the droids we're looking for...");
    }
    """.strip()
    actual = comby.rewrite(source, template, rewrite, language='.java')
    assert actual == expected


if __name__ == '__main__':
    logging.basicConfig()
    test_rewrite()
