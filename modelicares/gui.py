#!/usr/bin/python
"""Classes and functions to create a (limited) graphical user interface for
ModelicaRes
"""
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012-2013, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


import wx

from matplotlib import rcParams
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure

from modelicares.texunit import unit2tex


class PreviewPanel(wx.Panel):
    """Class that is a panel for information about a variable (used in
    :meth:`simres.SimRes.browse`)
    """
    def __init__(self, parent, id):

        # Change the matplotlb backend, but remember the original.
        orig_backend = rcParams['backend']
        rcParams['backend'] = 'WXAgg'

        wx.Panel.__init__(self, parent, id)
        txtpanel = wx.Panel(self, -1)

        self.display = wx.StaticText(txtpanel, -1, 'Click on a variable to '
            'list its attributes and plot its values.', (10,10),
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
            text = 'Name: "%s"' % name
            text += '\n' + 'Description: "%s"' % sim.get_description(name)
            text += '\n' + 'unit: "%s"' % sim.get_unit(name)
            text += '\n' + 'displayUnit: "%s"' % sim.get_displayUnit(name)
            self.display.SetLabel(text)
            self.axes.clear()
            self.axes.plot(sim.get_times(name), sim.get_values(name))
            self.axes.set_ylabel(name + " / $%s$" %
                                 unit2tex(sim.get_unit(name)))
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

    Initialization arguments:

    - *parent*: Parent frame

    - *id*: Indentification number

    - *sim*: Instance of :class:`simres.SimRes`
    """
    def __init__(self, parent, id, sim):

        def _build_tree(branches, branch):
            """Build the variable tree.
            """
            for key in branches.keys():
                data = wx.TreeItemData()
                if isinstance(branches[key], basestring):
                    data.SetData(branches[key])
                    subbranch = self.tree.AppendItem(branch, key, data=data)
                else:
                    data.SetData('')
                    subbranch = self.tree.AppendItem(branch, key, data=data)
                    _build_tree(branches[key], subbranch) # Recursion

        # Initial setup
        wx.Frame.__init__(self, parent, id, pos=wx.DefaultPosition,
                          size=wx.Size(800, 350))
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)
        panelL = wx.Panel(self, -1)
        self.panelR = PreviewPanel(self, -1)
        self.sim = sim

        # Add the tree.
        self.tree = wx.TreeCtrl(panelL, 1, wx.DefaultPosition, (-1, -1),
                                wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS)
        root = sim.nametree()
        _build_tree(root, self.tree.AddRoot(sim.fbase))

        # Bind events and finish.
        self.tree.Bind(wx.EVT_TREE_BEGIN_DRAG, self.OnDragInit)
        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged, id=1)
        vbox.Add(self.tree, 1, wx.EXPAND)
        hbox.Add(panelL, 2, wx.EXPAND)
        hbox.Add(self.panelR, 3, wx.EXPAND)
        panelL.SetSizer(vbox)
        self.SetSizer(hbox)
        self.Centre()

    def OnDragInit(self, event):
        """Drag the full variable name as text."""
        text = self.tree.GetItemData(event.GetItem()).GetData() + '\n'
        tdo = wx.TextDataObject(text)
        tds = wx.DropSource(self.tree)
        tds.SetData(tdo)
        tds.DoDragDrop(True)

    def OnSelChanged(self, event):
        """Update the variable's attributes and plot."""
        name = self.tree.GetItemData(event.GetItem()).GetData()
        self.panelR.preview(name, self.sim)

# Code below is based on http://code.google.com/p/easywx/, accessed 10/7/2012:
# easywx provides an easy-to-use interface for simple GUI interaction with a
# user.  It does not require the programmer to know anything about wxpython,
# frames, widgets, callbacks or lambda.  All GUI interactions are invoked by a
# simple function calls that return results.
#
# WARNING about using easywx with IDLE
# =====================================
#
# You may encounter problems using IDLE to run programs that use easywx.  Try
# it and find out.  easywx is a collection of Tkinter routines that run their
# own event loops.  IDLE is a wxpython application, with its own event loop.
# The two may conflict, with the unpredictable results. If you find that you
# have problems, try running your program outside of IDLE.
#
# Note that easywx requires wxPython release 2.8 or greater.

class mem:
    """Global memory class"""
    replyText = ''


class _ButtonBox(wx.Frame):
    """Dialog box with buttons
    """
    def __init__(self, *args, **kwargs):
        # Begin wxGlade: MyFrame.__init__
        kwargs["style"] = wx.DEFAULT_FRAME_STYLE
        message = kwargs.pop('msg')
        self.choices = kwargs.pop('choices')
        default = kwargs.pop('default')

        wx.Frame.__init__(self, *args, **kwargs)
        self.panel_1 = wx.Panel(self, -1)
        self.label_1 = wx.StaticText(self.panel_1, -1, "\n  %s  \n"%message)
        self.buttons = []
        self.Center()

        for i, choice in enumerate(self.choices):
            button = wx.Button(self.panel_1, -1, choice)
            button.Bind(wx.EVT_BUTTON, self.onClick)
            if i == default:
                button.SetDefault()
            self.buttons.append(button)

        self.__do_layout()
        # End wxGlade

    def onClick(self, event):
        """When clicked, remember the response.
        """
        mem.replyText = event.EventObject.Label
        self.Close()
        self.Destroy()

    def __do_layout(self):
        """Lay out the panels.
        """
        # Begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.GridSizer(1, len(self.buttons), 0, 0)
        sizer_2.Add(self.label_1, 0,
            wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 6)
        for button in self.buttons:
            sizer_3.Add(button, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|
                        wx.ALIGN_CENTER_VERTICAL, len(self.buttons))
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        self.panel_1.SetSizer(sizer_2)
        sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # End wxGlade
# End of class _ButtonBox


def buttonbox(msg="", title=" ", choices=("Button1", "Button2", "Button3"),
              default=None):
    """Display a message, title, and set of buttons.

    The buttons are defined by the members of the choices list.
    Return the text of the button that the user selected.

    @arg msg: the msg to be displayed.
    @arg title: the window title
    @arg choices: a list or tuple of the choices to be displayed
    """
    app = wx.GetApp()
    if app is None:
        app = wx.App()
    box = _ButtonBox(None, -1, title, msg=msg, choices=choices,
                     default=default)
    app.SetTopWindow(box)
    box.Show()
    app.MainLoop()
    app.Destroy()
    return mem.replyText


def msgbox(msg="(Your message goes here)", title=" ", ok_button="OK"):
    """Display a messagebox.
    """
    if type(ok_button) != type("OK"):
        raise AssertionError(
            "The 'ok_button' argument to msgbox must be a string.")
    return buttonbox(msg=msg, title=title, choices=[ok_button])


def boolbox(msg="Shall I continue?", title=" ", choices=("Yes","No"),
            default=None):
    """Display a boolean message box.

    The return value is 0 or 1 depending on the button.  If the dialog is
    cancelled, then *None* is returned.
    """
    return indexbox(msg, title, choices, default)


def indexbox(msg="Shall I continue?", title=" ", choices=("Yes","No"),
             default=None):
    """Display a button box with the specified choices.

    The return value is the index of the choice.  If the dialog is cancelled,
    then *None* is returned.
    """
    reply = buttonbox(msg, title, choices, default)
    for i, choice in enumerate(choices):
        if reply == choice:
            return i
    return None


def ynbox(msg="Shall I continue?", title=" ", choices=("Yes", "No"),
          default=None):
    """Display a msgbox with choices of Yes and No.

    The default is "Yes".

    The returned value is calculated this way::
        if the first choice ("Yes") is chosen, or if the dialog is cancelled:
            return 1
        else:
            return 0

    If invoked without a msg argument, displays a generic request for a
    confirmation that the user wishes to continue.  So it can be used this
    way::
        if ynbox(): pass # continue
        else: sys.exit(0)  # exit the program

    @arg msg: the msg to be displayed.
    @arg title: the window title
    @arg choices: a list or tuple of the choices to be displayed
    """
    return boolbox(msg, title, choices, default)


def ccbox(msg="Shall I continue?", title=" ", choices=("Continue", "Cancel"),
          default=None):
    """Display a msgbox with choices of Continue and Cancel.

    The default is "Continue".

    The returned value is calculated this way::
        if the first choice ("Continue") is chosen, or if the dialog is
        cancelled:
            return 1
        else:
            return 0

    If invoked without a msg argument, displays a generic request for a
    confirmation that the user wishes to continue.  So it can be used this
    way::

        if ccbox():
            pass # continue
        else:
            sys.exit(0)  # exit the program

    @arg msg: the msg to be displayed.
    @arg title: the window title
    @arg choices: a list or tuple of the choices to be displayed
    """
    return boolbox(msg, title, choices, default)
