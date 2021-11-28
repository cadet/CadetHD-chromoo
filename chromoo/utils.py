from cadet import Cadet
from functools import reduce
from addict import Dict

import numpy as np

import struct
from subprocess import run

from addict import Dict

def loadh5(filename):

    cadetpath = run(['which', 'cadet-cli'], capture_output=True, text=True ).stdout.strip()
    Cadet.cadet_path = cadetpath

    sim = Cadet()
    sim.filename = filename
    sim.load()

    return sim

def update_nested(refdict:dict, newdict:dict):
    """
    Update a dictionary in a nested manner.
    (Don't just overwrite top level key/values as is default behavior)
    """
    # FIXME:
    refdict = reconstruct(refdict)

    for key, value in newdict.items():
        if key in refdict.keys():
            if isinstance(value, dict):
                print(f"Nesting into {key}")
                update_nested(refdict[key], newdict[key])
            else:
                print(f"Assigning {key} {value}")
                refdict[key] = value
        else:
            print(f"Creating {key}")
            refdict.update({key: value})
    
    # print(refdict)
    return Dict(refdict)

def keystring_todict(key, value):
    """
        given a dot separated keystring and a value, convert them into a dict
        eg: (one.two.three, 3) -> {one: {two: {three: 3}}}

    """
    for item in reversed(key.split('.')):
        value = { item: value }

    return value

    
def reconstruct(dic:dict):
    """
    Convert from addict dict filled with numpy types to
    dict filled with python native types
    """
    # cleandict = {}
    dic = dict(dic)
    for key in dic.keys():
        if isinstance(dic[key], Dict):
            value = reconstruct(dic[key])
            # cleandict.update({key: value})
            dic.update({key: value})
        else:
            value = np2native(dic[key])
            # cleandict.update({key: value})
            dic.update({key: value})
    # return cleandict
    return dic


def np2native(obj):
    """
    Convert from numpy types to python native types
    """
    ENCODING = 'ascii'
    if isinstance(obj, bytes):
        return obj.decode(ENCODING)
    if isinstance(obj, np.bytes_):
        return obj.tobytes().decode(ENCODING)
    elif isinstance(obj,np.ndarray):
        if any(isinstance(x, bytes) for x in obj):
            return [ x.decode(ENCODING) for x in obj ]
        elif any(isinstance(x, np.bytes_) for x in obj):
            return [ x.tobytes().decode(ENCODING) for x in obj ]
        else:
            return obj.tolist()
    elif isinstance(obj, np.generic):
        return obj.tolist()
    else:
        return obj

def sse(y0, y):
    sse_value = sum([(n1 - n2)**2 for n1, n2 in zip(y, y0)])
    return sse_value


def deep_get(input_dict, keys, default=None, vartype=None, choices=[]):
    """
    Simpler syntax to get deep values from a dictionary
    > config.get('key1.key2.key3', defaultValue)

    - typechecking
    - value restriction
    """
    value = reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, keys.split("."), input_dict)

    if value is None:
        if default != None:
            # self.logger.warn(keys, 'not specified! Defaulting to', str(default) or 'None (empty string)')
            print(keys, 'not specified! Defaulting to', str(default) or 'None (empty string)')
            value = default

    if vartype:
        if not isinstance(value, vartype):
            # self.logger.die(keys, 'has invalid type!', str(type(value)), 'instead of', str(vartype))
            print(keys, 'has invalid type!', str(type(value)), 'instead of', str(vartype))
            raise(RuntimeError('Invalid vartype'))

    if choices:
        if value not in choices:
            # self.logger.die(keys, 'has invalid value! Must be one of ', str(choices))
            print(keys, 'has invalid value! Must be one of ', str(choices))
            raise(RuntimeError('Invalid choice'))

    return value


def readChromatogram(data_path):
    time= []
    conc= []
    delimiter = ' '
    with open(data_path, newline='') as csvfile:
        if ',' in csvfile.readline():
            delimiter = ','
    with open(data_path, newline='') as csvfile:
        # data = list(csv.reader(csvfile))
        for line in csvfile:
            data_line = line.strip().split(delimiter)
            data_line = list(filter(None, data_line))
            if (data_line != []):
                time.append(float(data_line[0]))
                conc.append(float(data_line[1]))
    return time, conc

def readArray(data_path):
    values =[]
    with open(data_path, newline='') as csvfile:
        for line in csvfile:
            values.append(float(line.strip()))
    return values


def dataformatsize(dataformat):
    vartype = dataformat[1]
    datasize = 0
    if vartype == 'd':
        datasize = 8
    elif vartype == 'f':
        datasize = 4
    elif vartype == 'i':
        datasize = 4
    return datasize

def bin_to_arr(filename, dataformat, skip=0, skiprows=0, nrows=0, ncols=0):
    datasize = dataformatsize(dataformat)

    with(open(filename, 'rb')) as input:
        input.seek(skip * nrows * ncols * datasize + skiprows * ncols * datasize, 0)
        myiter = struct.iter_unpack(dataformat, input.read())

        arr = []
        for i in myiter:
            arr.append(i[0])

        return arr

def create_h5_template(filename):
    """
    should:
        - load file
        - modify section times to match the ends of the csv data
        - modify simulation times to match
    """

    sim = loadh5(filename)

    t0, _ = readChromatogram("chromatogram-corrected.csv")

    ## NOTE: Adjust h5 times to use CSV times
    sim.root.input.solver.sections.section_times = [min(t0), max(t0)]
    sim.root.input.solver.user_solution_times = t0

    template_filename = f"{filename}_template.h5"
    sim.filename = template_filename
    sim.save()
    return template_filename
