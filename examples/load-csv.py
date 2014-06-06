#!/usr/bin/python
# Example of loading a CSV file using util.load_csv()

from modelicares import load_csv

if __name__=='__main__':

    fname = "load-csv.csv"
    data = load_csv(fname, header_row=2)
    print('Data has been loaded from "%s" into the "data" dictionary.'%fname)
    print("It contains these keys:")
    print(data.keys())
    print("Use the Python prompt to explore the data.")

    # Embed an IPython or standard Python interpreter.
    #    Based on
    #    http://writeonly.wordpress.com/2008/09/08/embedding-a-python-shell-in-a-python-script/,
    #    accessed 2010/11/2
    try:
        # IPython
        from IPython import embed
        embed()
    except ImportError:
        try:
            # IPython via old API style
            from IPython.Shell import IPShellEmbed
            IPShellEmbed(argv=['-noconfirm_exit'])()
            # Note: The -pylab option can't be embedded (see
            # http://article.gmane.org/gmane.comp.python.ipython.user/1190/match=pylab).
        except ImportError:
            # Standard Python
            from code import InteractiveConsole
            InteractiveConsole(globals()).interact()
