#!/usr/bin/python
"""Methods to format numbers to support LaTeX_

.. _LaTeX: http://www.latex-project.org/
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


def label_number(quantity="", unit=None, times='\,', per='\,/\,', roman=False):
    r"""Generate text to label a number as a quantity expressed in a unit.

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

    - *roman*: *True*, if the units should be typeset in Roman text (rather
      than italics)

    **Examples:**

       >>> label_number("Mobility", "m2/(V.s)", roman=True)
       'Mobility$\\,/\\,\\mathrm{m^{2}\\,V^{-1}\\,s^{-1}}$'

       in LaTeX_: Mobility :math:`\,/\,\mathrm{m^{2}\,V^{-1}\,s^{-1}}`

       >>> label_number("Mole fraction", "1")
       'Mole fraction'

    .. _Modelica: http://www.modelica.org/
    """
    if unit and unit != '1':
        return quantity + '$' + per + unit2tex(unit, times, roman) + '$'
    else:
        return quantity


def label_quantity(number, unit='', format='%G', times='\,', roman=False):
    r"""Generate text to label a quantity as a number times a unit.

    If an exponent is present, then either a LaTeX-formatted exponential or a
    System International (SI) prefix is applied.

    **Arguments:**

    - *number*: Floating point or integer number

    - *unit*: String specifying the unit

         *unit* uses extended Modelica_ notation.  See :meth:`unit2tex`.

    - *format*: Modified Python_ number formatting string

         If LaTeX-formatted exponentials should be applied, then then use an
         uppercase exponential formatter ('E' or 'G').  A lowercase exponential
         formatter ('e' or 'g') will result in a System International (SI)
         prefix, if applicable.

         .. Seealso::
            http://docs.python.org/release/2.5.2/lib/typesseq-strings.html
            and http://en.wikipedia.org/wiki/SI_prefix

    - *times*: LaTeX_ math string to indicate multiplication

         *times* is applied between the number and the first unit and between
         units.  The default is 3/18 quad space.  The multiplication between
         the significand and the exponent is always indicated by
         ":math:`\times`".

    - *roman*: *True*, if the units should be typeset in Roman text (rather
      than italics)

    **Examples:**

       >>> label_quantity(1.2345e-3, 'm', format='%.3e', roman=True)
       '1.234$\\,\\mathrm{mm}$'

       in LaTeX_: :math:`1.234\mathrm{\,mm}`

       >>> label_quantity(1.2345e-3, 'm', format='%.3E', roman=True)
       '1.234$\\times10^{-3}$$\\,\\mathrm{m}$'

       in LaTeX_: :math:`1.234\times10^{-3}\,\mathrm{m}`

       >>> label_quantity(1.2345e6)
       '1.2345$\\times10^{6}$'

       in LaTeX_: :math:`1.2345\times10^{6}`

       >>> label_quantity(1e3, '\Omega', format='%.1e', roman=True)
       '1.0$\\,\\mathrm{k\\Omega}$'

       in LaTeX_: :math:`1.0\,\mathrm{k\Omega}`

    .. _Python: http://www.python.org/
    """
    def _si_prefix(pow1000):
        """Return the SI prefix for a power of 1000.
        """
        # Prefixes according to Table 5 of BIPM 2006
        # (http://www.bipm.org/en/si/si_brochure/; excluding hecto, deca, deci,
        # and centi).
        try:
            return ['Y', # yotta (10^24)
                    'Z', # zetta (10^21)
                    'E', # exa (10^18)
                    'P', # peta (10^15)
                    'T', # tera (10^12)
                    'G', # giga (10^9)
                    'M', # mega (10^6)
                    'k', # kilo (10^3)
                    '', # (10^0)
                    'm', # milli (10^-3)
                    r'{\mu}', # micro (10^-6)
                    'n', # nano (10^-9)
                    'p', # pico (10^-12)
                    'f', # femto (10^-15)
                    'a', # atto (10^-18)
                    'z', # zepto (10^-21)
                    'y'][8 - pow1000] # yocto (10^-24)
        except IndexError:
            print("The factor 1e%i is beyond the range covered by the SI "
                  "prefixes (1e-24 to 1e24)." % 3*pow1000)
            raise

    # Apply engineering notation and SI prefixes.
    if 'E' in format:
        use_SI = False
        format = format.replace('E', 'e')
    elif 'G' in format:
        use_SI = False
        format = format.replace('G', 'g')
    else:
        use_SI = True

    # Format the number as a string.
    numstr = format % number

    # Use LaTeX formatting or SI prefixes if an exponent is present.
    try: # to format the exponent in LaTeX.
        significand, exponent = numstr.split('e')
        if use_SI:
            e = int(exponent)
            if e >= 0:
                pow1000 = e/3
            else:
                pow1000 = -(-e/3)
            pow1000 = int(pow1000) # TODO:  Why is this necessary in Python 3?
            if -8 <= pow1000 <= 8:
                unit = _si_prefix(pow1000) + unit
                numstr, exponent = (format % (number/1000**pow1000)).split('e')
        if not use_SI or exponent != '+00': # Use LaTeX formatting.
            exponent = (exponent[0] + exponent[1:].lstrip('0')).lstrip('+')
            numstr = significand + r'$\times10^{' + exponent + '}$'
    except:
        pass # since no exponent.
    if unit:
        return numstr + '$\,' + unit2tex(unit, times, roman) + '$'
    else:
        return numstr


def unit2tex(unit, times='\,', roman=False):
    r"""Convert a Modelica_ unit string to LaTeX.

    **Arguments:**

    - *unit*: Unit string in extended Modelica_ notation

        .. Seealso:: Modelica Specification, version 3.2, p. 209
           (https://www.modelica.org/documents)

           In summary, '.' indicates multiplication.  The denominator is
           enclosed in parentheses and begins with a '/'.  Exponents directly
           follow the significand (e.g., no carat ('^')).

       Here, the unit may also contain LaTeX_ math mode commands.  For example,
       '\\Omega' becomes :math:`\Omega`.  Use '\\%' for percent, '\\$' for
       dollar, and '\\mathrm{^{\\circ}C}' for degree Celsius
       (:math:`\mathrm{^{\circ}C}`).  Use '$' in pairs (without a leading '\\')
       to escape and then return to the LaTeX_ math mode later in the string.
       Use '\\!' to cancel a 3/18 quad space ('\\,').

    - *times*: LaTeX_ math string to indicate multiplication

         *times* is applied between the number and the first unit and between
         units.  The default is 3/18 quad space.

    - *roman*: *True*, if the units should be typeset in Roman text (rather
      than italics)

    **Example:**

       >>> unit2tex("m/s2", roman=True)
       '\\mathrm{m\\,s^{-2}}'

       which will render in LaTeX_ math as :math:`\mathrm{m\,s^{-2}}`
    """
    # Special characters that should be passed through directly
    EXCEPTIONS = ['%',    # Percent
                  '$',    # US dollar or beginning/end of LaTeX math string
                  '^',    # Used in degree Celcius
                  '\x5c', # Beginning of LaTeX command, "\"
                  '{',    # Beginning of LaTeX math group
                  '}',    # End of LaTeX math group
                  ',',    # Used in inserting a positive 3/18 quad space
                  '!',    # Used in inserting a negative 3/18 quad space
                  ]

    def _simple_unit2tex(unit, is_numerator=True, times=r'\,'):
        """Convert the numerator or denominator of a Modelica_ unit to LaTeX.
        """
        if unit == '1':
            return ''
        tex = ''
        exponent = ''
        pointer = 0
        while pointer < len(unit):
            # Skip the exceptions.
            while (pointer < len(unit) and (unit[pointer].isalpha() or
                                            unit[pointer] in EXCEPTIONS)):
                tex += unit[pointer]
                pointer += 1
            # Handle the exponents.
            while pointer < len(unit) and unit[pointer].isdigit():
                exponent += unit[pointer]
                pointer += 1
            if exponent:
                if is_numerator:
                    tex += '^{' + exponent + '}'
                else:
                    tex += '^{-' + exponent + '}'
                exponent = ''
            elif not is_numerator:
                tex += '^{-1}'
                exponent = ''
            # Replace the next dot ('.') with times.
            if pointer < len(unit) - 1:
                if unit[pointer] == '.':
                    tex += times
                else:
                    print('The unit part %s has an unexpected character '
                          '"%s".  It will be skipped.' % (unit, unit[pointer]))
                pointer += 1
            elif pointer == len(unit) - 1:
                print('The unit part "%s" is terminated by an unexpected '
                      'character.  It will be skipped.' % unit)
                break
        return tex

    if unit:
        while '..' in unit:
            print('There are double dots in unit "%s".  Only one '
                  'muliplication string will be added.' % unit)
            unit = unit.replace('..', '.')

        # Split the numerator and the denominator.
        if '/' in unit:
            numerator, denominator = unit.split('/', 1)
            if denominator.startswith('(') and denominator.endswith(')'):
                denominator = denominator[1:-1]
            unit = (_simple_unit2tex(numerator, times=times) + times +
                    _simple_unit2tex(denominator, is_numerator=False,
                                     times=times))
        else:
            unit = _simple_unit2tex(unit, times=times)
        if roman:
            unit = '\mathrm{%s}' % unit
    return unit


if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
