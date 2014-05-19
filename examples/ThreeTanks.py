
           >>> from modelicares import SimRes, save

           >>> sim = SimRes('examples/ThreeTanks')
           >>> sankeys = sim.sankey(label='examples/ThreeTanks',
           ...     title="Sankey Diagrams of Modelica.Fluid.Examples.Tanks.ThreeTanks",
           ...     times=[0, 50, 100, 150], n_rows=2, format='%.1f ',
           ...     names=['tank1.ports[1].m_flow', 'tank2.ports[1].m_flow',
           ...            'tank3.ports[1].m_flow'],
           ...     labels=['Tank 1', 'Tank 2', 'Tank 3'],
           ...     orientations=[-1, 0, 1],
           ...     scale=0.1, margin=6, offset=1.5,
           ...     pathlengths=2, trunklength=10)
           >>> save()
           Saved examples/ThreeTanks.pdf
           Saved examples/ThreeTanks.png

        .. testsetup::
           >>> import matplotlib.pyplot as plt
           >>> plt.show()
           >>> plt.close()

        .. only:: html

           .. image:: ../examples/ThreeTanks.png
              :scale: 70 %
              :alt: Sankey digarams of three-tank model

        .. only:: latex

           .. figure:: ../examples/ThreeTanks.pdf
              :scale: 70 %

              Sankey digarams of three-tank model