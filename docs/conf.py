# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

cwd = os.getcwd()
project_root = os.path.dirname(cwd)
src_root = os.path.join(project_root, "src")
sys.path.insert(0, project_root)

import markus  # noqa


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Markus"
copyright = "2017-2022, Will Kahn-Greene"
author = "Will Kahn-Greene"

# The short X.Y version.
version = markus.__version__
# The full version, including alpha/beta/rc tags.
release = "%s %s" % (markus.__version__, markus.__releasedate__)


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.doctest", "sphinx.ext.autodoc"]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

html_sidebars = {
    "**": ["about.html", "navigation.html", "relations.html", "searchbox.html"]
}
