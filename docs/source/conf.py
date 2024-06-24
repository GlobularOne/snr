import sys
import pathlib
import sphinx.highlighting
from snr.cli.lexer import SnrLexer

sys.path.insert(0, str(pathlib.Path(__file__).parents[2] / "snr"))

project = 'snr'
copyright = '2024, GlobularOne'
author = 'GlobularOne'

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.todo",
    "sphinx.ext.napoleon",
    "sphinx_rtd_theme"
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

todo_include_todos = True

highlight_language = "snr"
sphinx.highlighting.lexers['snr'] = SnrLexer()
