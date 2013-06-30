#!/usr/bin/python
"""Update the ReST README from the Markdown README.
"""

import pypandoc

readme = pypandoc.convert('README.md', 'rst')
f = open('README.txt', 'w')
f.write(readme)
f.close()
