#!/usr/bin/python
"""Functions to format numbers to support LaTeX_

- :meth:`number_label` - Return a string to indicate a quantity in a unit

- :meth:`quantity_str` - Return a string to represent a quantity as a number
  times a unit

- :meth:`unit2tex` - Convert a Modelica_ unit string to LaTeX_


.. _LaTeX: http://www.latex-project.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"


import re

from modelicares.util import si_prefix, get_pow1000

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915,
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=C0103, W0622

# Special replacements for unit strings in tex
REPLACEMENTS = [(re.compile(replacement[0]), replacement[1])
                for replacement in
                [('degC', r'^{\circ}C'),
                 ('degF', r'^{\circ}F'),
                 ('%', r'\%'),
                 ('ohm', r'\Omega'),
                 ('angstrom', r'\AA'),
                 ('pi', r'\pi'),
                 ('alpha', r'\alpha'),
                 ('Phi', r'\Phi'),
                 ('mu', r'\mu'),
                 ('epsilon', r'\epsilon')]]


def number_label(quantity="", unit=None, times=r'\,', per=r'\,/\,',
                 roman=False):
    r"""Return a string to label a number, specifically a quantity in a unit

    The unit is formatted with LaTeX_ as needed.

    **Arguments:**

    - *quantity*: String describing the quantity

    - *unit*: String specifying the unit

         This is expressed in extended Modelica_ notation.  See
         :meth:`unit2tex`.

    - *times*: LaTeX_ math string to indicate multiplication

         *times* is applied between the number and the first unit and between
         units.  The default is 3/18 quad space.  The multiplication between
         the significand and the exponent is always indicated by
         ":math:`\times`".

    - *per*: LaTeX_ math string to indicate division

         It is applied between the quantity and the units.  The default is a
         3/18 quad space followed by '/; and another 3/18 quad space.  The
         division associated with the units on the denominator is always
         indicated by a negative exponential.

         If the unit is not a simple scaling factor, then "in" is used instead.
         For example,

            >>> number_label("Gain", "dB")
            'Gain in $dB$'

    - *roman*: *True*, if the units should be typeset in Roman (rather than
      italics)

    **Examples:**

       >>> number_label("Mobility", "m2/(V.s)", roman=True)
       'Mobility$\\,/\\,\\mathrm{m^{2}\\,V^{-1}\\,s^{-1}}$'

       in LaTeX_: Mobility :math:`\,/\,\mathrm{m^{2}\,V^{-1}\,s^{-1}}`

       >>> number_label("Mole fraction", "1")
       'Mole fraction'

    .. _Modelica: http://www.modelica.org/
    """
    if unit in ['dB', 'degC', 'degF', 'Pag', 'kPag']:
        return "%s in $%s$" % (quantity, unit2tex(unit, times, roman))
    if unit and unit != '1':
        return quantity + '$' + per + unit2tex(unit, times, roman) + '$'
    else:
        return quantity

def quantity_str(number, unit='', use_si=True, format='%g', times=r'\,',
                 roman=True):
    r"""Generate a string to write a quantity as a number times a unit.

    If an exponent is present, then either a LaTeX-formatted exponential or a
    System International (SI) prefix is applied.

    **Arguments:**

    - *number*: Floating point or integer number

    - *unit*: String specifying the unit

         *unit* uses extended Modelica_ notation.  See :meth:`unit2tex`.

    - *use_si*: *True*, if SI prefixes should be used

    - *format*: Modified Python_ number formatting string

         .. Seealso::
            http://docs.python.org/release/2.5.2/lib/typesseq-strings.html
            and http://en.wikipedia.org/wiki/SI_prefix

    - *times*: LaTeX_ math string to indicate multiplication

         *times* is applied between the number and the first unit and between
         units.  The default is 3/18 quad space.  The multiplication between
         the significand and the exponent is always indicated by
         ":math:`\times`".

    - *roman*: *True*, if the units should be typeset in Roman (rather than
      Italics)

    **Examples:**

       >>> quantity_str(1.2345e-3, 'm', format='%.3f')
       '1.234$\\,\\mathrm{mm}$'

       in LaTeX_: :math:`1.234\mathrm{\,mm}`

       >>> quantity_str(1.2345e-3, 'm', use_si=False, format='%.3e')
       '1.234$\\times10^{-3}$$\\,\\mathrm{m}$'

       in LaTeX_: :math:`1.234\times10^{-3}\,\mathrm{m}`

       >>> quantity_str(1.2345e6)
       '1.2345$\\times10^{6}$'

       in LaTeX_: :math:`1.2345\times10^{6}`

       >>> quantity_str(1e3, '\Omega', format='%.1f')
       '1.0$\\,\\mathrm{k\\Omega}$'

       in LaTeX_: :math:`1.0\,\mathrm{k\Omega}`


    .. _Python: http://www.python.org/
    """
    # Factor out powers of 1000 if SI prefixes will be used.
    if use_si and unit:
        pow1000 = max(min(get_pow1000(number), 8), -8)
        number /= 1000**pow1000
        unit = si_prefix(pow1000) + unit

    # Format the number as a string.
    numstr = format % number
    numstr = numstr.replace('E', 'e')

    # Use LaTeX formatting for scientific notation.
    try:
        significand, exponent = numstr.split('e')
    except ValueError:
        pass # No exponent
    else:
        numstr = significand + r'$\times10^{%i}$' % int(exponent)

    # Return the number with the unit.
    if unit:
        return numstr + r'$' + times + unit2tex(unit, times, roman) + '$'
    else:
        return numstr


def unit2tex(unit, times=r'\,', roman=False):
    r"""Convert a Modelica_ unit string to LaTeX_.

    **Arguments:**

    - *unit*: Unit string in extended Modelica_ notation

        .. Seealso:: Modelica Specification, version 3.2, p. 209
           (https://www.modelica.org/documents)

           In summary, '.' indicates multiplication.  The denominator is
           enclosed in parentheses and begins with a '/'.  Exponents directly
           follow the significand (e.g., no carat ('^')).

    - *times*: LaTeX_ math string to indicate multiplication

         *times* is applied between the number and the first unit and between
         units.  The default is 3/18 quad space.

    - *roman*: *True*, if the units should be typeset in Roman (rather than
      italics)

    **Example:**

       >>> unit2tex("m/s2", roman=True)
       '\\mathrm{m\\,s^{-2}}'

       which will render in LaTeX_ math as :math:`\mathrm{m\,s^{-2}}`
    """
    splitter = re.compile('([^0-9+-]*)(.*)')

    def _process_unit(unit, is_numerator):
        """Convert a simple Modelica_ unit to LaTeX.
        """
        if unit == '1' or not unit:
            return ''
        tex, exponent = splitter.match(unit).groups()
        if exponent:
            tex += ('^{%s}' if is_numerator else '^{-%s}') % exponent
        elif not is_numerator:
            tex += '^{-1}'
        return tex

    def _process_group(unit, times=r'\,', is_numerator=True):
        """Convert the numerator or denominator of a Modelica_ unit to LaTeX.
        """
        if unit.startswith('('):
            assert unit.endswith(')'), ("The unit group %s starts with '(' but "
                                        "does not end with ')'." % unit)
            unit = unit[1:-1]
        texs = [_process_unit(u, is_numerator) for u in unit.split('.')]
        return times.join(texs)

    if unit:
        # Split the numerator and the denominator.
        if '/' in unit:
            try:
                numerator, denominator = unit.split('/')
            except ValueError:
                raise ValueError("Check that the unit string %s has at most "
                                 "one division sign." % unit)
            unit = (_process_group(numerator, times) + times +
                    _process_group(denominator, times, is_numerator=False))
        else:
            unit = _process_group(unit, times)

        # Make the special replacements.
        for rpl in REPLACEMENTS:
            unit = rpl[0].sub(rpl[1], unit)

        if roman:
            unit = r'\mathrm{%s}' % unit

    return unit


if __name__ == '__main__':
    # Test the contents of this file.

    import doctest
    doctest.testmod()
