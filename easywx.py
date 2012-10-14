# Based on http://code.google.com/p/easywx/, accessed 10/7/12
"""
easywx provides an easy-to-use interface for simple GUI interaction with a user.
It does not require the programmer to know anything about wxpython, frames,
widgets, callbacks or lambda.  All GUI interactions are invoked by a simple
function calls that return results.

WARNING about using easywx with IDLE
=====================================

You may encounter problems using IDLE to run programs that use easywx.  Try it
and find out.  easywx is a collection of Tkinter routines that run their own
event loops.  IDLE is a wxpython application, with its own event loop.  The two
may conflict, with the unpredictable results. If you find that you have
problems, try running your program outside of IDLE.

Note that easywx requires wxPython release 2.8 or greater.
"""
__version__ = "0.1 modified KLD 2012-10-09"

import wx, sys, os

_replyText = "notdefined"
_app = None
def SetGlobals():
    global _app
    if not _app:
        _app = wx.App(False)

# buttonbox
class _ButtonBox(wx.Frame):
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
        global _replyText
        _replyText = event.EventObject.Label
        self.Close()
        self.Destroy()

    def __do_layout(self):
        # Begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.GridSizer(1, len(self.buttons), 0, 0)
        sizer_2.Add(self.label_1, 0,
                    wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 6)
        for button in self.buttons:
            sizer_3.Add(button, 0,
                        wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL,
                        len(self.buttons))
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
    SetGlobals()
    global _replyText
    box = _ButtonBox(None, -1, title, msg=msg, choices=choices, default=default)
    _app.SetTopWindow(box)
    box.Show()
    _app.MainLoop()
    return _replyText

# msgbox
def msgbox(msg="(Your message goes here)", title=" ", ok_button="OK"):
    """Display a messagebox.
    """
    if type(ok_button) != type("OK"):
        raise AssertionError("The 'ok_button' argument to msgbox must be a string.")
    return buttonbox(msg=msg, title=title, choices=[ok_button])

# boolbox
def boolbox(msg="Shall I continue?", title=" ", choices=("Yes","No"),
            default=None):
    """Display a boolean message box.

    The return value is 0 or 1 depending on the button.  If the dialog is
    cancelled, then *None* is returned.
    """
    return indexbox(msg, title, choices, default)

# indexbox
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

# ynbox
def ynbox(msg="Shall I continue?", title=" ", choices=("Yes", "No"),
          default=None):
    """Display a msgbox with choices of Yes and No.

    The default is "Yes".

    The returned value is calculated this way::
        if the first choice ("Yes") is chosen, or if the dialog is cancelled:
            return 1
        else:
            return 0

    If invoked without a msg argument, displays a generic request for a confirmation
    that the user wishes to continue.  So it can be used this way::
        if ynbox(): pass # continue
        else: sys.exit(0)  # exit the program

    @arg msg: the msg to be displayed.
    @arg title: the window title
    @arg choices: a list or tuple of the choices to be displayed
    """
    return boolbox(msg, title, choices, default)

# ccbox
def ccbox(msg="Shall I continue?", title=" ", choices=("Continue", "Cancel"),
          default=None):
    """Display a msgbox with choices of Continue and Cancel.

    The default is "Continue".

    The returned value is calculated this way::
        if the first choice ("Continue") is chosen, or if the dialog is cancelled:
            return 1
        else:
            return 0

    If invoked without a msg argument, displays a generic request for a confirmation
    that the user wishes to continue.  So it can be used this way::

        if ccbox():
            pass # continue
        else:
            sys.exit(0)  # exit the program

    @arg msg: the msg to be displayed.
    @arg title: the window title
    @arg choices: a list or tuple of the choices to be displayed
    """
    return boolbox(msg, title, choices, default)
