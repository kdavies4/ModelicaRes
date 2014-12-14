#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Context managers to be used as simulators

In general, the context managers are used like this:

.. code-block:: python

   >>> with context_manager() as simulator: # doctest: +SKIP
   ...     simulator.run(model, params)

For more details, see the documentation for each context manager below:

- :class:`dymola_script` - Write a Dymola\ :sup:`®`-formatted simulation script

- :class:`dymosim` - Run executable models from Dymola\ :sup:`®`

- :class:`FMI` - Simulate FMUs_ via PyFMI_


.. _FMUs: https://www.fmi-standard.org/
.. _PyFMI: TODO
"""

import os

from datetime import date
from .. import ParamDict
from ..util import expand_path, flatten_dict


class _GenericSimulator(object):
    """Base class for all context managers to be used as simulators

    **Parameters:**

    - \*\**options*: Additional keyword arguments for the simulator
    """

    def __init__(self, **options):
        """Upon initialization, store the simulation options.

        See the top-level class documentation.
        """
        self._options = options

        # Start counting the experiments.
        self.n_experiments = 0
        self._exp_list = open("experiment_list.txt", 'w')


    def __enter__(self):
        """Enter the context of the simulator.
        """
        # Everything has been done in __init__.
        return self


    def __exit__(self, *exc_details):
        """Exit the context of the simulator.
        """
        self._exp_list.close()


    def __getattr__(self, attr):
        """If an unknown attribute is requested, look for it in the dictionary
        of simulation options.
        """
        return self._options[attr]


    def __setattr__(self, attr, value):
        """If an unknown attribute is set, add it to the dictionary of
        simulation options.
        """
        self._options[attr] = value


class dymola_script(object):

    """Context manager to write a Dymola\ :sup:`®`-formatted simulation script

    **Initialization parameters (defaults in parentheses):**

    - *fname* ("run_sims.mos"): Name of the script file to be written, relative
      to the current directory

    - *command* ('simulateModel'): Simulation or other command to
      Dymola\ :sup:`®`

         Besides 'simulateModel', this can be 'linearizeModel' to create a state
         space representation or 'translateModel' to create model executables
         without running them.

    - *results* (['dsin.txt', 'dslog.txt', 'dsres.mat', 'dymosim%x',
      'dymolalg.txt']): List of files to copy to the results folder

         Each entry is the path/name of a file that is generated during
         simulation.  The path is relative to the working directory.  '%x' may
         be included in the filename to represent '.exe' if the operating system
         is Windows and '' otherwise.  The result folders are named by the
         number of the experiment and placed within the folder contains the
         simulation script (*fname*).

    - *working_dir* (*None*): Working directory where the executable, log files,
      etc. are initially created

         '~' may be included to represent the user directory.  Use *None* for
         the current directory.

    - *packages* ([]): List of Modelica_ packages that should be preloaded or
      scripts that should be run before the simulation experiments

         Each may be a "\*.mo" file, a folder that contains a "package.mo" file,
         or a "\*.mos" file.  The path may be absolute or relative to
         *working_dir*.  The Modelica Standard Library does not need to be
         included since it is loaded automatically.  If an entry is a script
         ("\*.mos"), it is run from its folder.

    - \*\**options*: Additional keyword arguments for *command*

         If *command* is 'simulateModel', then the following keywords may be
         used.  The defaults (shown in parentheses) are applied by
         Dymola\ :sup:`®`, not by this context manager.

         - *startTime* (0): Start of simulation

         - *stopTime* (1): End of simulation

         - *numberOfIntervals* (0): Number of output points

         - *outputInterval* (0): Distance between output points

         - *method* ("Dassl"): Integration method

         - *tolerance* (0.0001): Tolerance of integration

         - *fixedstepsize* (0): Fixed step size for Euler

         - *resultFile* ("dsres.mat"): Where to store result

    **Example 1 (single simulation):**

    .. code-block:: python

       >>> from modelicares.exps.simulators import dymola_script

       >>> with dymola_script("examples/ChuaCircuit/run_sims1.mos",
       ...                    stopTime=2500) as simulator:
       ...     simulator.run('Modelica.Electrical.Analog.Examples.ChuaCircuit')

    In *examples/ChuaCircuit/run_sims1.mos*:

    .. code-block:: modelica

       // Modelica experiment script written by modelicares ...
       import Modelica.Utilities.Files.copy;
       import Modelica.Utilities.Files.createDirectory;
       Advanced.TranslationInCommandLog = true "Also include translation log in command log";
       cd(".../Documents/Modelica");
       destination = ".../examples/ChuaCircuit/";

       // Experiment 1
       ok = simulateModel(problem="Modelica.Electrical.Analog.Examples.ChuaCircuit", stopTime=2500);
       if ok then
           savelog();
           createDirectory(destination + "1");
           copy("dsin.txt", destination + "1/dsin.txt", true);
           copy("dslog.txt", destination + "1/dslog.txt", true);
           copy("dsres.mat", destination + "1/dsres.mat", true);
           copy("dymosim", destination + "1/dymosim...", true);
           copy("dymolalg.txt", destination + "1/dymolalg.txt", true);
       end if;
       clearlog();

       exit();

    where "..." depends on the local system.

    **Example 2 (simulating with different options):**

    The simulation options can also be set after establishing the context.

    .. code-block:: python

       >>> from modelicares.exps.simulators import dymola_script

       >>> with dymola_script("examples/ChuaCircuit/run_sims2.mos") as simulator:
       ...     simulator.stopTime = 250
       ...     simulator.run('Modelica.Electrical.Analog.Examples.ChuaCircuit')
       ...     simulator.stopTime = 2500
       ...     simulator.run('Modelica.Electrical.Analog.Examples.ChuaCircuit')

    The second simulation is the same as in Example 1.

    **Example 3 (full-factorial design of experiments):**

    Multiple parameters can be adjusted using functions from the
    :mod:`~modelicares.exps.doe` module.

    .. code-block:: python

       >>> from modelicares.exps.simulators import dymola_script
       >>> from modelicares.exps import doe

       >>> with dymola_script("examples/ChuaCircuit/run_sims3.mos") as simulator:
       ...     experiments = doe.fullfact({'L.L': [18, 20],
       ...                                 'C1.C': [8, 10],
       ...                                 'C2.C': [80, 100, 120]})
       ...     for experiment in experiments:
       ...         simulator.run("Modelica.Electrical.Analog.Examples.ChuaCircuit",
       ...                       params=experiment)

    In *examples/ChuaCircuit/run_sims3.mos*, there are commands to run and save
    results from twelve simulations.
    """

    def __init__(self, fname="run_sims.mos", command='simulateModel',
                 results=['dsin.txt', 'dslog.txt', 'dsres.mat', 'dymosim%x',
                          'dymolalg.txt'],
                 working_dir=None, packages=[], **options):
        """Upon initialization, start writing the simulation script.

        See the top-level class documentation.
        """

        # Preprocess the arguments.
        fname = expand_path(fname)
        if working_dir is None:
            working_dir = os.getcwd()
        else:
            working_dir = expand_path(working_dir)
        results_dir = os.path.dirname(fname)
        exe = '.exe' if os.name == 'nt' else ''
        for i, result in enumerate(results):
            results[i] = result.replace('%x', exe)
        self._results = results
        self._options = options

        # Open the script.
        print("Starting to write the Dymola simulation script...")
        mos = open(fname, 'w')
        self._mos = mos

        # Write the header.
        mos.write('// Modelica experiment script written by modelicares %s\n'
                  % date.isoformat(date.today()))
        mos.write('import Modelica.Utilities.Files.copy;\n')
        mos.write('import Modelica.Utilities.Files.createDirectory;\n')
        mos.write('Advanced.TranslationInCommandLog = true "Also include '
                  'translation log in command log";\n')
        mos.write('cd("%s");\n' % working_dir)
        for package in packages:
            if package.endswith('.mos'):
                mos.write('cd("%s");\n' % os.path.dirname(package))
                mos.write('RunScript("%s");\n' % os.path.basename(package))
            else:
                if package.endswith('.mo'):
                    mos.write('openModel("%s");\n' % package)
                else:
                    mos.write('openModel("%s");\n' % os.path.join(package,
                                                                  'package.mo'))
                mos.write('cd("%s");\n' % working_dir)
        mos.write('destination = "%s";\n'
                  % (os.path.normpath(results_dir) + os.path.sep))
        mos.write('\n')
        # Sometimes Dymola opens with an error; simulate any model to clear the
        # error.
        # mos.write('simulateModel("Modelica.Electrical.Analog.Examples.'
        #           'ChuaCircuit");\n\n')


    def __enter__(self):
        """Enter the context of the simulator.
        """
        # Everything has been done in __init__.
        return self


    def __exit__(self, *exc_details):
        """Exit the context of the simulator.
        """
        # Exit the simulation environment.
        # Otherwise, the script will hang until it is closed manually.
        self._mos.write("exit();\n")
        self._mos.close()

        self._exp_list.close()
        print("Finished writing the Dymola simulation script.")


    def run(self, model=None, params={}):
        """Write commands to run and save the results of a single experiment.

        **Parameters:**

        - *model*: String representing the name of the model, including the full
          path in Modelica_ dot notation

             If *model* is *None*, then the model is not included in the
             command.  Dymola\ :sup:`®` will use the last translated model.

        - *params*: Dictionary of parameter names and values to be set within
          the model

             The keys or variable names in this dictionary must indicate the
             hierarchy within the model---either in Modelica_ dot notation or
             via nested dictionaries.  If *model* is *None*, then *params* is
             ignored.  Python_ values are automatically represented in Modelica_
             syntax (see :meth:`~modelicares.exps.ParamDict.__str__`).
             Redeclarations and other prefixes must be included in the keys
             along with the class names (e.g.,
             ``{'redeclare package Medium': 'Modelica.Media.Air.MoistAir'}``).

             Any item with a value of *None* is skipped.
        """

        # Record this simulation experiment in the list of experiments.
        self.n_experiments += 1
        entry = '%s:  %s%s' % (n_experiments, model, params)
        self._exp_list.write(entry)
        print(entry)

        # Write the command to run the model.
        mos = self._mos
        mos.write('// Experiment %i\n' % experiment_count)
        command = self._command
        options = self._options
        if model:
            problem = '"%s%s"' % (model, ParamDict(flatten_dict(params)))
            mos.write('ok = %s%s;\n' % (command, ParamDict(options,
                                                           problem=problem)))
        else:
            mos.write('ok = %s%s;\n' % (command, ParamDict(options)))

        # Write the commands to save the results.
        mos.write('if ok then\n')
        mos.write('    savelog();\n')
        folder = str(self.n_experiments)
        mos.write('    createDirectory(destination + "%s");\n' % folder)
        for result in self._results:
            mos.write('    copy("%s", destination + "%s", true);\n' %
                      (result, os.path.join(folder, result)))
        mos.write('end if;\n')

        # Write the command to clear the log file.
        mos.write('clearlog();\n\n')


class dymosim(object):

    """Context manager to run executable models from Dymola\ :sup:`®`

    .. Warning:: This context manager has not been implemented yet.

    **Initialization parameters (defaults in parentheses):**

    - *results* (['dsin.txt', 'dslog.txt', 'dsres.mat', 'dymosim%x',
      'dymolalg.txt']): List of files to copy to the results folder

         Each entry is the path/name of a file that is generated during
         simulation.  The path is relative to the working directory.  '%x' may
         be included in the filename to represent '.exe' if the operating system
         is Windows and '' otherwise.  The result folders are named by the
         number of the experiment and placed within the folder contains the
         simulation script (*fname*).

    **Example:**

    >>> from modelicares.exps import doe
    >>> from modelicares.exps.simulators import dymola_executable

    >>> with dymola_executable() as simulator:
    ...     for experiment in doe.ofat(TODO):
    ...         simulator.run(*experiment)
    """

    def __init__(self,
                 results=['dsin.txt', 'dslog.txt', 'dsres.mat', 'dymolalg.txt'],
                 **options):
        """Upon initialization, establish some settings.

        See the top-level class documentation.
        """
        _GenericSimulator.__init__(self, **options)
        raise NotImplementedError(
            "The dymosim context manager has not yet been implemented.")


    def run(self, model, params={}):
        r"""Run and save the results of a single experiment.

        .. Warning:: This function has not been implemented yet.

        **Parameters:**

        - *model*: String representing the name of the model, including the full
          path in Modelica_ dot notation

             If *model* is *None*, then the model is not included in the
             command.  Dymola\ :sup:`®` will use the last translated model.

        - *params*: Dictionary of parameter names and values to be set within
          the model

             The keys or variable names in this dictionary must indicate the
             hierarchy within the model---either in Modelica_ dot notation or
             via nested dictionaries.  If *model* is *None*, then *params* is
             ignored.  Python_ values are automatically represented in Modelica_
             syntax (see :meth:`~modelicares.exps.ParamDict.__str__`).
             Redeclarations and other prefixes must be included in the keys
             along with the class names (e.g.,
             ``{'redeclare package Medium': 'Modelica.Media.Air.MoistAir'}``).

             Any item with a value of *None* is skipped.

        - *experiments*: Tuple or (list or generator of) tuples specifying the
          simulation experiment(s)

             The first entry of each tuple is the name of the model executable.
             The second is a dictionary of model parameter names and values.  The
             third is a dictionary of simulation settings (keyword and value).

             Each tuple may be (optionally) an instance of the tuple subclass
             :class:`Experiment`, which names the entries as *model*, *params*, and
             *options*.  These designations are used below for clarity.

             *model* may include the file path.  It is not necessary to include the
             extension (e.g., ".exe").   There must be a corresponding model
             initialization file on the same path with the same base name and the
             extension ".in".  For Dymola\ :sup:`®`, the executable is the
             "dymosim" file (possibly renamed) and the initialization file is a
             renamed 'dsin.txt' file.

             The keys or variable names in the *params* dictionary must indicate
             the hierarchy within the model---either in Modelica_ dot notation or
             via nested dictionaries.  The items in the dictionary must correspond
             to parameters in the initialization file.  In Dymola, these are
             integers or floating point numbers.  Therefore, arrays must be broken
             into scalars by indicating the indices (Modelica_ 1-based indexing) in
             the key along with the variable name.  Enumerations and Booleans must
             be given as their unsigned integer equivalents (e.g., 0 for *False*).
             Strings and prefixes are not supported.

             Items with values of *None* in *params* and *options* are skipped.

'%x' may
         be included in the filename to represent '.exe' if the operating system
         is Windows and '' otherwise.


        **Example:**

        .. code-block:: python

           >>> from modelicares.exps.simulators import dymosim

           >>> with dymosim(stopTime=2500) as simulator:
           ...     simulator.run('examples/ChuaCircuit%x')

        For more complicated scenarios, use the same form as in examples 2 and 3
        in the :class:`dymola_script` documentation.

        **Examples:**
    import os

    from itertools import count, product

    model = 'Modelica.Mechanics.MultiBody.Examples.Systems.RobotR3.oneAxis'
    params = {'axis.motor.i_max': [5, 9, 15],
              'axis.motor.Ra.R': [200, 250, 300]}
    params = {'axis.motor.i_max': 9,
              'axis.motor.Ra.R': 250}
    params = {'L.L': [18, 20],
              'C1.C': [8, 10],
              'C2.C': [80, 100, 120]}


    doe = gen_doe(params)
    for e in doe:
       print(str(e) + ' or ' + modifier(e))

    params.items()

    simspecs = [SimSpec(model + "(L(L=%s), C1(C=%s), C2(C=%s))" % params,
                resultFile="ChuaCircuit%i" % i)
                for i, params in zip(count(1), product(Ls, C1s, C2s))]
        """
        pass


class FMI(object):

    """Context manager to simulate FMUs_ via PyFMI_

    .. Warning:: This context manager has not been implemented yet.

    **Example:**

    .. code-block:: python

       >>> from modelicares.exps.simulators import FMI

       >>> with FMI(stopTime=2500) as simulator:
       ...     simulator.run('examples/ChuaCircuit.fmu')

    For more complicated scenarios, use the same form as in examples 2 and 3
    in the :class:`dymola_script` documentation.
    """

    def __init__(self, *args, **kwargs):
        raise NotImplementedError(
            "The FMI context manager hasn't been implemented yet.")


    def run(self, model, params={}):
        r"""Run and save the results of a single experiment.

        .. Warning:: This function has not been implemented yet.
        """
        pass
