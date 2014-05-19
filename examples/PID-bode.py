           
        .. code-block:: python

           >>> from modelicares import LinRes, save
           >>> from numpy import pi, logspace

           >>> lin = LinRes('examples/PID.mat')
           >>> lin.bode(label='examples/PID-bode', omega=2*pi*logspace(-2, 3),
           ...          title="Bode Plot of Modelica.Blocks.Continuous.PID") # doctest: +ELLIPSIS
           (<matplotlib.axes...AxesSubplot object at 0x...>, <matplotlib.axes...AxesSubplot object at 0x...>)
           >>> save()
           Saved examples/PID-bode.pdf
           Saved examples/PID-bode.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()