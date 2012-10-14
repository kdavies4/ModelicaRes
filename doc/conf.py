# -*- coding: utf-8 -*-
#
# FCSys User's Guide build configuration file, created by sphinx-quickstart for
# matplotlib and modified.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed
# automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import sys, os

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#sys.path.append(os.path.abspath('sphinxext'))

def setup(app):
    app.add_javascript('copybutton.js')

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.autodoc']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = 'FCSys Utilities'
copyright = '2012 (Kevin Davies).  Documentation scripts from matplotlib v1.2'

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
import fcres
version = fcres.__version__
# The full version, including alpha/beta/rc tags.
release = version

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
unused_docs = []

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# Options for HTML output
# -----------------------

# Theme or style
html_theme = 'sphinxdoc'

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project + " v" + version + " User's Guide"
#html_title = None

# The name of an image file (within the static path) to place at the top of
# the sidebar.
html_logo = 'logo.gif'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If nonempty, this is the file name suffix for generated HTML files.  The
# default is ``".html"``.
html_file_suffix = '.html'

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Content template for the index page
#html_index = 'index.html'

# Custom sidebar templates, maps document names to template names
html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {'index': 'index.html'}

# If false, no module index is generated.
html_use_modindex = True

# If true, the reST sources are included in the HTML build as _sources/<name>.
#html_copy_source = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.
html_use_opensearch = 'False'

# Output file base name for HTML help builder.
htmlhelp_basename = 'FCSysUtilitiesDoc'

math_output = 'MathML'

# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
latex_font_size = '11pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).

latex_documents = [
  ('index', 'FCSysUtilities.tex', r"FCSys Utilities User's Guide", 'Kevin Davies', 'manual'),
]

latex_elements = { 'classoptions': ',openany,openside',
                   'babel' : '\\usepackage[english]{babel}' }

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = '_static/logo.png'

# Additional stuff for the LaTeX preamble.
latex_preamble = """
   \usepackage{amsmath}
   \usepackage{amsfonts}
   \usepackage{amssymb}
   \usepackage{txfonts}
"""

# Documents to append as an appendix to all manuals.
latex_appendices = []

# If false, no module index is generated.
latex_use_modindex = True

# If true, the topmost sectioning unit is parts, else it is chapters
#latex_use_parts = True

# Show both class-level docstring and __init__ docstring in class
# documentation
autoclass_content = 'both'

rst_epilog = """"""
