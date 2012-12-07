#!/usr/bin/python
# Copied (and cleaned up slightly) from
# http://code.activestate.com/recipes/286150-hierarchical-data-objects/,
# accessed 10/31/11
__author__ = "Kevin Davies"
__email__ = "kdavies4@gmail.com"
__copyright__ = "Copyright 2012, Georgia Tech Research Corporation"
__license__ = "BSD-compatible (see LICENSE.txt)"


class HierarchicalData(object):
    """Organize hierarchical data as a tree.

    For convenience, inner nodes need not be constructed explicitly.  See
    examples below.
    """

    def __init__(self):
        # self._d stores subtrees
        self._d = {}

    def __getattr__(self, name):
        # Only attributes not starting with "_" are organized in the tree.
        if not name.startswith("_"):
            return self._d.setdefault(name, HierarchicalData())
        raise AttributeError("Object %r has no attribute %s" % (self, name))

    def __getstate__(self):
        # For pickling
        return self._d, self._attributes()

    def __setstate__(self, tp):
        # For unpickling
        d,l = tp
        self._d = d
        for name,obj in l: setattr(self, name, obj)

    def _attributes(self):
        """Return 'leaves' of the data tree.
        """
        return [(s, getattr(self, s)) for s in dir(self) if not s.startswith("_") ]

    def _getLeaves(self, prefix=""):
        # getLeaves tree, starting with self
        # prefix stores name of tree node above.
        prefix = prefix and prefix + "."
        rv = {}
        atl = self._d.keys()
        for at in atl:
            ob = getattr(self, at)
            trv = ob._getLeaves(prefix+at)
            rv.update(trv)
        for at, ob in self._attributes():
            rv[prefix+at] = ob
        return rv

    def __str__(self):
        # Easy to read string representation of data
        rl = []
        for k,v in self._getLeaves().items():
            rl.append("%s = %s" %  (k,v))
        return "\n".join(rl)

def getLeaves(ob, pre=""):
    """Return dictionary mapping paths from root to leafs to value of leafs.
    """
    return ob._getLeaves(pre)

if __name__=="__main__":
    """Demonstrate the HierarchialData class.
    """
    import pickle

    model = HierarchicalData()

    # model.person is constructed on the fly:
    model.person.surname = "uwe"
    model.person.name = "schmitt"
    model.number = 1

    print("Access via attributes:\n")
    print("model.person.surname=", model.person.surname)
    print("model.person.name=", model.person.name)
    print("model.number=", model.number)

    print("\nPrint complete model:\n")
    print(model)

    o = pickle.loads(pickle.dumps(model))

    print("\nUnpickle after pickle:\n")
    print(o)
    print("\nPaths from root to leaves and values at leaves:\n")
    print(getLeaves(o))
