        .. code-block:: python

           >>> import os

           >>> from glob import glob
           >>> from modelicares import LinRes, multinyquist, save, read_params
           >>> from numpy import pi, logspace

           >>> lins = LinRes('examples/PID/*/*.mat')
           >>> labels = ["Td=%g" % read_params('Td', os.path.join(lin.dir, 'dsin.txt'))
           ...           for lin in lins]
           >>> multinyquist(title="Nyquist Plot of Modelica.Blocks.Continuous.PID",
           ...              label='examples/PIDs-nyquist', textFreq=True,
           ...              omega=2*pi*logspace(-1, 3, 81), labelFreq=20,
           ...              labels=labels) # doctest: +ELLIPSIS
           <matplotlib.axes...AxesSubplot object at 0x...>

           >>> save()
           Saved examples/PIDs-nyquist.pdf
           Saved examples/PIDs-nyquist.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()