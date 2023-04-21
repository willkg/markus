============
Contributing
============

How to help
===========

Markus is used in production in a few places, but I'd love to know how
you use Markus and how Markus' API works for you. Is it easy? Are there 
thing that are hard?

If you encounter any bugs, please write up an issue in the issue tracker.


Writing up issues
=================

Please write up issues in the `issue tracker
<https://github.com/willkg/markus/issues>`_.

If the issue is about a bug in Markus, please specify:

1. the version of Markus that you're using
2. the version of Python that you're using
3. the traceback and error message if applicable

These things will help me figure out the problem faster.


Install for hacking
===================

Run::

    # Clone the repository
    $ git clone https://github.com/willkg/markus

    # Create a virtualenvironment
    ...

    # Install Markus and dev requirements
    $ pip install -r requirements-dev.txt


Documentation
=============

Documentation is written in reStructuredText and is in the ``docs/``
directory. We use `Sphinx <http://www.sphinx-doc.org/en/stable/>`_
to build documentation.


Tests
=====

Run tests with `tox <https://tox.readthedocs.io/en/latest/>`_. This
will run all tests across all supported Python versions.

Tests are located in the ``tests/`` directory.
