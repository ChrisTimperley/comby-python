.. -*-restructuredtext-*-

comby-python
============


.. image:: https://travis-ci.org/ChrisTimperley/comby.svg?branch=master
    :target: https://travis-ci.org/ChrisTimperley/comby

.. image:: https://badge.fury.io/py/comby.svg
    :target: https://badge.fury.io/py/comby

.. image:: https://img.shields.io/pypi/pyversions/comby.svg
    :target: https://pypi.org/project/comby

Python bindings for `Comby <https://github.com/comby-tools/comby>`_.


Installation
------------

Comby must be installed: https://github.com/comby-tools/comby

To install the latest release from PyPI:

.. code:: shell

   $ pip install comby 

or to install from source:

.. code:: shell

   $ pip install .


Getting Started
---------------

To perform a basic match-rewrite on a given source text:

.. code:: python

   from comby import Comby

   comby = Comby()
   match = 'print :[[1]]'
   rewrite = 'print(:[1])'
   source_old = 'print "hello world"'
   source_new = comby.rewrite(source_old, match, rewrite)
   # -> 'print("hello world")
