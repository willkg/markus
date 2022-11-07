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


Release process
===============

1. Checkout main tip and create a prep branch like ``2_0_0_prep``.

2. Check to make sure ``setup.py`` and requirements are updated.

   Update dev dependencies: ``make checkrot``

3. Update version numbers in ``src/markus/__init__.py``.

   1. Set ``__version__`` to something like ``0.4.0`` (use semver).
   2. Set ``__releasedate__`` to something like ``20120731``.

4. Update ``HISTORY.rst``

   1. Set the date for the release.
   2. Make sure to note any backwards incompatible changes.

5. Verify correctness.

   1. Check manifest: ``check-manifest``
   2. Run tests: ``make test``
   3. Lint: ``make lint``
   4. Build docs (this runs example code).

6. Push that branch and create a PR. If that passes, then merge it.

7. Check out and update main branch locally.

8. Tag the release::

       $ git tag -s v0.4.0

   Copy details from ``HISTORY.rst`` into the tag comment.

9. Update PyPI--do this in a Python3 virtualenv::

        $ rm -rf dist/*
        $ python setup.py sdist bdist_wheel
        $ twine upload dist/*

10. Push everything::

       $ git push --tags origin main

11. Announce the release with a blog post and tweet.
