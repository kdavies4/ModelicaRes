#!/usr/bin/python
"""Shortcuts to the "get" methods in :class:`SimRes`

**Example:**

.. code-block:: python

   >>> from modelicares import SimRes
   >>> from modelicares.simres.info import *

   >>> sim = SimRes('examples/ChuaCircuit.mat')
   >>> values(sim, 'L.v') # doctest: +ELLIPSIS
   array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)

This is the same as

.. code-block:: python

   >>> sim.get_values('L.v') # doctest: +ELLIPSIS
   array([  0.00000000e+00, ... -2.53528625e-01], dtype=float32)
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


from . import SimRes


description = SimRes.get_description
"""Alias for :meth:`SimRes.get_description`"""
displayUnit = SimRes.get_displayUnit
"""Alias for :meth:`SimRes.get_displayUnit`"""
indices_wi_times = SimRes.get_indices_wi_times
"""Alias for :meth:`SimRes.get_indices_wi_times`"""
IV = SimRes.get_IV
"""Alias for :meth:`SimRes.get_IV`"""
FV = SimRes.get_FV
"""Alias for :meth:`SimRes.get_FV`"""
times = SimRes.get_times
"""Alias for :meth:`SimRes.get_times`"""
unit = SimRes.get_unit
"""Alias for :meth:`SimRes.get_unit`"""
values = SimRes.get_values
"""Alias for :meth:`SimRes.get_values`"""
values_at_times = SimRes.get_values_at_times
"""Alias for :meth:`SimRes.values_at_times`"""

if __name__ == '__main__':
    """Test the contents of this file."""
    import doctest
    doctest.testmod()
    exit()
