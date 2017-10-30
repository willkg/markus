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

Documentation is written in restructuredText and is in the ``docs/``
directory. We use `Sphinx <http://www.sphinx-doc.org/en/stable/>`_
to build documentation.


Tests
=====

Tests are run using the `py.test <http://pytest.org/>`_ test runner.

Tests are located in the ``tests/`` directory.


Release process
===============

1. Checkout master tip.

2. Check to make sure ``setup.py`` and requirements files
   have correct versions of requirements.

3. Update version numbers in ``markus/__init__.py``.

   1. Set ``__version__`` to something like ``0.4``.
   2. Set ``__releasedate__`` to something like ``20120731``.

4. Update ``HISTORY.rst``

   1. Set the date for the release.
   2. Make sure to note any backwards incompatible changes.

5. Verify correctness.

   1. Run tests.
   2. Build docs (this runs example code).
   3. Verify all that works.

6. Tag the release::

       $ git tag -a v0.4

   Copy the details from ``HISTORY.rst`` into the tag comment.

7. Push everything::

       $ git push --tags official master

8. Update PyPI::

       $ rm -rf dist/*
       $ python setup.py sdist bdist_wheel
       $ twine upload dist/*

9. Announce the release.
