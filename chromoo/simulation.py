import copy
import random
import string
import subprocess
from pathlib import Path

from chromoo.utils import keystring_todict, deep_get, sse, readChromatogram, readArray
import numpy as np
import os

def run_and_eval(x, sim, parameters, objectives, name=None, tempdir=Path('temp'), store=False ) -> list :
    sim = run_sim(x, sim, parameters, name=name, tempdir=tempdir, store=store)
    sses = evaluate_sim(sim, objectives)
    return sses



def run_sim(x, sim, parameters, name=None, tempdir=Path('temp'), store=False):
    """
        - run one simulation
        - calculate and return scores
    """
    newsim = copy.deepcopy(sim)

    if name:
        newsim.filename = name
    else:
        newsim.filename = tempdir.joinpath('temp' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6)) + '.h5')

    update_sim_parameters(newsim, x, parameters)

    newsim.save()

    try:
        newsim.run(check=True)
    except subprocess.CalledProcessError as error:
        print(f"{newsim.filename} failed: {error.stderr.decode('utf-8').strip()}")
        print(f"Parameters: {x}\n")
        raise(RuntimeError("Simulation Failure"))

    newsim.load()

    if not store:
        os.remove(newsim.filename)

    return newsim

def evaluate_sim(newsim, objectives):
    sses = []

    # FIXME: Make generic scores
    
    objectives_contain_times = True
    if objectives[0].get('times'):
        objectives_contain_times = False

    for obj in objectives:
        y = deep_get(newsim.root, obj.path)
        y = np.array(y).flatten()
        if objectives_contain_times:
            _, y0 = readChromatogram(obj.filename)
        else:
            y0 = readArray(obj.filename)

        sses.append(sse(y0, y))

    return sses

def update_sim_parameters(sim, x, parameters):
    # For every parameter, generate a dictionary based on the path, and
    # update the simulation in a nested way
    # TODO: Probably a neater way to do this

    prev_len = 0
    for p in parameters:
        cur_len = p.get('length')

        if p.index != 0:
            arr = sim.root
            for key in p.path.split('.'):
                arr = arr[key]
            assert(p.length == 1)
            value = x[prev_len : prev_len + cur_len]
            arr[p.index] = value
            cur_dict = keystring_todict(p.get('path'), arr)
        else:
            cur_dict = keystring_todict(p.get('path'), x[prev_len : prev_len + cur_len])

        sim.root.update(cur_dict)
        prev_len += p.get('length')
