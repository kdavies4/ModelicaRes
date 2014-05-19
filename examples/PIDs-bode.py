
           >>> import os

           >>> from glob import glob
           >>> from modelicares import LinRes, multibode, save, read_params
           >>> from numpy import pi, logspace

           >>> lins = LinRes('examples/PID/*/*.mat')
           >>> labels = ["Ti=%g" % read_params('Ti', os.path.join(lin.dir, 'dsin.txt'))
           ...           for lin in lins]
           >>> multibode(title="Bode Plot of Modelica.Blocks.Continuous.PID",
           ...           label='examples/PIDs-bode', omega=2*pi*logspace(-2, 3),
           ...           labels=labels, leg_kwargs=dict(loc='lower right')) # doctest: +ELLIPSIS
           (<matplotlib.axes...AxesSubplot object at 0x...>, <matplotlib.axes...AxesSubplot object at 0x...>)

           >>> save()
           Saved examples/PIDs-bode.pdf
           Saved examples/PIDs-bode.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()