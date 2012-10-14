The "control" folder is a slightly modified version of the python-control module
(http://sourceforge.net/apps/mediawiki/python-control).  If it is changed or
updated to a new distribution version, it must be rebuilt using the following
    $ cd FCSys/resources/code/Python/control
    $ python setup.py build
    $ sudo python setup.py install
or the same from the FCSys/install directory (which will rebuild and reinstall
other modules too):
    $ cd FCSys/install
    $ python setup.py build
    $ sudo python setup.py install
