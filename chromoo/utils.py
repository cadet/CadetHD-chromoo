from functools import reduce
from matplotlib import pyplot as plt


def keystring_todict(key, value):
    """
        given a dot separated keystring and a value, convert them into a dict
        eg: (one.two.three, 3) -> {one: {two: {three: 3}}}

    """
    for item in reversed(key.split('.')):
        value = { item: value }

    return value

def sse(y0, y):
    """
        calculate the SSE given 2 vectors
    """
    return sum([(n1 - n2)**2 for n1, n2 in zip(y, y0)])

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
    """
        Read chromatogram files in csv, or space-delimited format
        Return two vectors: time, concentration
    """
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
    """
        Read a text file with one value per line into a list
    """
    values =[]
    with open(data_path, newline='') as csvfile:
        for line in csvfile:
            values.append(float(line.strip()))
    return values

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
