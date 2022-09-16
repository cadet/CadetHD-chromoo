from numpy import log10
import numpy as np
from pymoo.core.individual import Individual
from pymoo.core.population import Population

def lognorm(array, mins, maxs):
    logs = log10(array)
    logmins = log10(mins)
    logmaxs = log10(maxs)

    return normalize(logs, logmins, logmaxs)

def lognorm_inverse(array, mins, maxs):
    logmins = log10(mins)
    logmaxs = log10(maxs)

    deno = denormalize(array, logmins, logmaxs)
    return np.power(10, deno)

def normalize(array, mins, maxs):
    return (array - mins) / (maxs - mins)

def denormalize(array, mins, maxs):
    return array * (maxs - mins) + mins

def identity(array, *args, **kwargs):
    return array

transforms = {
    'lognorm' : {
        'transform': lognorm,
        'inverse': lognorm_inverse
    },
    'normalize': {
        'transform': normalize,
        'inverse': denormalize
    },
    'none': {
        'transform': identity,
        'inverse': identity
    }
}

def transform_array(arrays, mins, maxs, transform, mode='transform'):
    """
    mode = 'inverse' or 'transform' allows bidirectional mapping
    """
    return transforms[transform][mode](arrays, mins, maxs)

# TODO: Numpy-ify
def transform_population(population:Population, mins, maxs, transform, mode='transform'):
    """
    mode = 'inverse' or 'transform' allows bidirectional mapping
    """
    return np.fromiter(map(lambda p: Individual(X=transforms[transform][mode](p.X, mins, maxs), F=p.F), population), Individual)

