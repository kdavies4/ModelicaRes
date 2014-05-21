Glossary
========

These terms appear in the documentation and may need clarification:

   **attribute** - a variable, method, or other entity of an object

   **constant** - a variable that is not time-varying [1]_

   **method** - a function bound to an object

   **object** - an instance of a class; an abstraction for data

   **variable** - an instance of :class:`~modelicares.simres.Variable` that
   contains information about units, description, times, and values of a
   Modelica_ variable, constant, or parameter over the course of a simulation;
   may be constant or time-varying

   **variable name** - a string representing a scalar variable in a Modelica_
   model; includes path separators (dots) and if applicable, indices within an
   array


.. [1] This definition differs from the Modelica_ definition because it
   encompasses parameters and variables without a ``constant`` or ``parameter``
   prefix, as long as they do not change over time.  In the post-processing of
   Modelica_ simulation results, it may not be possible to determine if a
   variable is a Modelica_ ``constant``, but it is possible to check if it
   changes over time.

.. _Modelica: http://www.modelica.org/
