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
copyright = "2017-2024, Will Kahn-Greene"
author = "Will Kahn-Greene"

version = markus.__version__
release = version


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.doctest", "sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- autodoc configuration
autoclass_content = "both"
autodoc_typehints = "description"


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]

html_sidebars = {
    "**": ["about.html", "navigation.html", "relations.html", "searchbox.html"]
}
