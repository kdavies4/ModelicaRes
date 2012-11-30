#!/usr/bin/python
"""Set up Modelica_ simulations and load, analyze, and plot the results.

This module provides direct access to the most important functions and classes
from its submodules.  These are:

- Basic supporting classes and functions: :meth:`base.add_arrows`,
  :meth:`base.add_hlines`, :meth:`base.add_vlines`, :meth:`base.animate`,
  :class:`base.ArrowLine`, :meth:`base.closeall`, :meth:`base.figure`,
  :meth:`base.load_csv`, :meth:`base.saveall`, :meth:`base.setup_subplots`

- To manage simulation experiments:  :class:`exps.Experiment`,
  :meth:`exps.gen_experiments`, :class:`exps.ParamDict`,
  :meth:`exps.read_params`, :meth:`exps.run_models`, :meth:`exps.write_params`,
  :meth:`exps.write_script`

- To handle multiple files at once: :meth:`multi.multiload`,
  :meth:`multi.multiplot`

- For linearization results: :class:`linres.LinRes`

- For linearization results: :class:`simres.SimRes`

- To label numbers and quantities: :meth:`texunit.label_number`,
  :meth:`texunit.label_quantity`, :meth:`texunit.unit2tex`

.. _Modelica: http://www.modelica.org/
"""
__author__ = "Kevin Davies"
__version__ = "0.1"
__email__ = "kdavies4@gmail.com"
# Copyright (c) 2010-2012, Kevin Davies
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#    * Neither the name of the <organization> nor the names of its contributors
#      may be used to endorse or promote products derived from this software
#      without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#__all__ = ['base', 'exps', 'linres', 'multi', 'simres', 'texunit']

# Essential functions and classes
#
# These will be available directly from modelicares; others must be loaded from
# their submodules.
from base import (add_arrows, add_hlines, add_vlines, animate, ArrowLine,
                 closeall, figure, load_csv, saveall, setup_subplots)
from exps import (Experiment, gen_experiments, ParamDict, read_params,
                  run_models, write_params, write_script)
from multi import multiload, multiplot
from linres import LinRes
from simres import SimRes
from texunit import label_number, label_quantity, unit2tex
