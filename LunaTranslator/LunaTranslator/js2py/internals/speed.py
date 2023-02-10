from __future__ import print_function

from timeit import timeit
from collections import namedtuple
from array import array
try:
    #python 2 code
    from itertools import izip as zip
except ImportError:
    pass

from collections import deque


class Y(object):
    UUU = 88

    def __init__(self, x):
        self.x = x

    def s(self, x):
        return self.x + 1


class X(Y):
    A = 10
    B = 2
    C = 4
    D = 9

    def __init__(self, x):
        self.x = x
        self.stack = []
        self.par = super(X, self)

    def s(self, x):
        pass

    def __add__(self, other):
        return self.x + other.x

    def another(self):
        return Y.s(self, 1)

    def yet_another(self):
        return self.par.s(1)


def add(a, b):
    return a.x + b.x


t = []

Type = None
try:
    print(timeit(
        """

t.append(4)
t.pop()



""",
        "from __main__ import X,Y,namedtuple,array,t,add,Type, zip",
        number=1000000))
except:
    raise
