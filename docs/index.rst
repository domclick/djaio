.. Djaio documentation master file, created by
   sphinx-quickstart on Tue Nov  1 22:07:24 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Djaio
=====

Djaio is an asynchronous web framework. It is a lightweight Django-like wrap over the ``aiohttp`` framework.
It can be used as usual application server, e.g. for building REST-APIs.

Prerequisites
-------------

Djaio requires Python 3.5 or higher.

Installation
------------

The package is not awailable in PyPi yet, so you can install it using git::

    $ pip install git+https://github.com/Sberned/djaio.git@0.0.4#egg=djaio

Alternatively you can download `source code <https://github.com/Sberned/djaio/archive/0.0.4.zip>`_, unzip it
and run ``setup.py`` from the root of unpacked folder.

Tutorial
--------

Now you are ready to bootstrap your web service by the following tutorial.

    #. :doc:`tutorial/01-application`
    #. :doc:`tutorial/02-views-and-methods`

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

