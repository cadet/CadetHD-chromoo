from functools import reduce
from matplotlib import pyplot as plt
from typing import TypeVar, Callable, Any, Optional, overload
import itertools as it

import numpy as np

T = TypeVar("T")

def keystring_todict(key, value):
    """
        given a dot separated keystring and a value, convert them into a dict
        eg: (one.two.three, 3) -> {one: {two: {three: 3}}}

    """
    for item in reversed(key.split('.')):
        value = { item: value }

    return value

# Overloaded to ensure typing is properly specified.
# deep_get, when called with vartype, will always ensure return type is that of vartype.

@overload
def deep_get(input_dict:dict, keys:str, vartype:Callable[[Any], T], default=None, choices=[]) -> T: ...

@overload
def deep_get(input_dict:dict, keys:str, vartype:None=None, default=None, choices=[]) -> Any: ...

def deep_get(input_dict:dict, keys:str, vartype:Optional[Callable[[Any], T]] = None, default=None, choices=[]) -> Optional[T]: 

    value = reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, keys.split("."), input_dict)

    if value is None:
        if default != None:
            # self.logger.warn(keys, 'not specified! Defaulting to', str(default) or 'None (empty string)')
            print(keys, 'not specified! Defaulting to', str(default) or 'None (empty string)')
            value = default

    if choices:
        if value not in choices:
            # self.logger.die(keys, 'has invalid value! Must be one of ', str(choices))
            print(keys, 'has invalid value! Must be one of ', str(choices))
            raise(RuntimeError('Invalid choice'))

    if vartype is not None and vartype is not Any:
        if value is not None: 
            return vartype(value)

    return value

def readChromatogram(data_path, delimiter=','):
    """
        Read chromatogram files in csv, or space-delimited format
        Return two vectors: time, concentration
    """
    arr = np.loadtxt(data_path, delimiter=delimiter).T
    return arr[0], arr[1]

def readArray(data_path):
    """
        Read a text file with one value per line into a list
    """
    return np.loadtxt(data_path)

def plotter(sim, objectives):
    """
        Given a simulation dict, and objectives, plot the final values and targets
    """
    for obj in objectives:
        fig, ax = plt.subplots()

        ## FIXME
        if obj.times:
            c0 = readArray(obj.filename)
            t0 = readArray(obj.times)
        else:
            t0, c0 = readChromatogram(obj.filename)

        t1 = sim.root.output.solution.solution_times
        c1 = deep_get(sim.root, obj.path)

        ax.plot(t0,c0, lw=1, ls='solid', label='reference')
        ax.plot(t1,c1, lw=1, ls='dashed', label='result')

        ax.set(title=obj.name)
        fig.savefig(f"chromoo_{obj.name}_result.png")

def pairwise(iterable):
    """ Given an iterable, return a set of pairwise tuples. This is added to itertools in 3.10 """
    # pairwise('ABCDEFG') --> AB BC CD DE EF FG
    a, b = it.tee(iterable)
    next(b, None)
    return zip(a, b)
