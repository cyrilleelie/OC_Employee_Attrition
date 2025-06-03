# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Attrition RH API'
copyright = '2025, Cyrille ELIE'
author = 'Cyrille ELIE'
release = 'v0.2.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',      # Pour inclure la documentation des docstrings
    'sphinx.ext.napoleon',     # Pour supporter les docstrings style Google/NumPy
    'sphinx.ext.viewcode',     # Pour ajouter des liens vers le code source
    'sphinx_rtd_theme',        # Pour le thème Read the Docs
    'autoapi.extension',       # Pour sphinx-autoapi
    'myst_parser',             # Pour écrire des pages en Markdown
]

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'markdown', # ou restructuredtext
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = []

language = 'fr'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

autoapi_type = 'python'
autoapi_dirs = ['../../src'] # Chemin vers votre code source depuis conf.py
autoapi_options = [
    'members', 
    'undoc-members', # Inclut même les membres sans docstring (pour voir ce qui manque)
    'show-inheritance',
    'show-module-summary',
    'imported-members'
]
autoapi_keep_files = True # Garde les fichiers .rst générés par autoapi (utile pour déboguer)
autoapi_add_toctree_entry = True # Ajoute automatiquement les pages générées au toctree
