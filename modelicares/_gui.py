#!/usr/bin/python
"""Classes to create a simple graphical user interface for ModelicaRes
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = ("Copyright 2012-2014, Kevin Davies, Hawaii Natural Energy "
                 "Institute, and Georgia Tech Research Corporation")
__license__ = "BSD-compatible (see LICENSE.txt)"


import wx

from matplotlib import rcParams
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from six import string_types

from modelicares.texunit import unit2tex

# Standard pylint settings for this project:
# pylint: disable=I0011, C0302, C0325, R0903, R0904, R0912, R0913, R0914, R0915,
# pylint: disable=I0011, W0141, W0142

# Other:
# pylint: disable=E1101

class PreviewPanel(wx.Panel):
    """Panel for information about a variable
    """
    def __init__(self, parent, id_num):

        # Change the matplotlib backend, but remember the original.
        orig_backend = rcParams['backend']
        rcParams['backend'] = 'WXAgg'

        wx.Panel.__init__(self, parent, id_num)
        txtpanel = wx.Panel(self, -1)

        self.display = wx.StaticText(txtpanel, -1,
                                     "Click on a variable to list its "
                                     "attributes and plot its values.\n"
                                     "You can also drag variable name into a "
                                     "text document.", (10, 10),
                                     style=wx.ALIGN_LEFT)
        self.figure = Figure(figsize=(2, 2))
        self.figure.subplots_adjust(left=0.17, right=0.95, bottom=0.15,
                                    top=0.95)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(txtpanel, 1, wx.EXPAND)
        self.sizer.Add(self.canvas, 3, wx.EXPAND)
        self.SetSizerAndFit(self.sizer)

        # Return to the original setting.
        rcParams['backend'] = orig_backend

    def preview(self, name, sim):
        """Show the variable's attributes and a small plot."""
        self.axes.clear()
        if name:
            text = 'Name: %s' % name
            text += '\n' + 'Description: %s' % sim[name].description
            text += '\n' + 'unit: %s' % sim[name].unit
            text += '\n' + 'displayUnit: %s' % sim[name].displayUnit
            self.display.SetLabel(text)
            self.axes.clear()
            self.axes.plot(sim[name].times(), sim[name].values())
            self.axes.set_ylabel(name + " / $%s$" %
                                 unit2tex(sim[name].unit))
            self.axes.set_xlabel("Time / s")
        else:
            self.display.SetLabel("")
        self.canvas.draw()

    def clear(self):
        """Clear the text and the plot."""
        self.axes.clear()
        self.canvas.draw()


class Browser(wx.Frame):
    """Class to browse the variables of a simulation (used in
    :meth:`simres.SimRes.browse`)

    **Initialization arguments:**

    - *parent*: Parent frame

    - *id_num*: Indentification number

    - *sim*: Instance of :class:`simres.SimRes`
    """
    # pylint: disable=C0103

    def __init__(self, parent, id_num, sim):

        def _build_tree(branches, branch):
            """Build the variable tree.
            """
            for key in branches.keys():
                data = wx.TreeItemData()
                if isinstance(branches[key], string_types):
                    data.SetData(branches[key])
                    subbranch = self.tree.AppendItem(branch, key, data=data)
                else:
                    data.SetData('')
                    subbranch = self.tree.AppendItem(branch, key, data=data)
                    _build_tree(branches[key], subbranch) # Recursion

        # Initial setup
        wx.Frame.__init__(self, parent, id_num, pos=wx.DefaultPosition,
                          size=wx.Size(800, 350))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panel_left = wx.Panel(self, -1)
        self.panel_right = PreviewPanel(self, -1)
        self.sim = sim

        # Add the tree.
        self.tree = wx.TreeCtrl(panel_left, 1, wx.DefaultPosition, (-1, -1),
                                wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        root = sim.nametree()
        _build_tree(root, self.tree.AddRoot(sim.fbase))

        # Bind events and finish.
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragInit)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        vbox.Add(self.tree, 1, wx.EXPAND)
        hbox.Add(panel_left, 2, wx.EXPAND)
        hbox.Add(self.panel_right, 3, wx.EXPAND)
        panel_left.SetSizer(vbox)
        self.SetSizer(hbox)
        self.Centre()

    def OnDragInit(self, event):
        """Drag the full variable name as text.
        """
        text = self.tree.GetItemData(event.GetItem()).GetData() + '\n'
        tdo = wx.TextDataObject(text)
        tds = wx.DropSource(self.tree)
        tds.SetData(tdo)
        tds.DoDragDrop(True)

    def OnSelChanged(self, event):
        """Update the variable's attributes and plot.
        """
        name = self.tree.GetItemData(event.GetItem()).GetData()
        self.panel_right.preview(name, self.sim)
