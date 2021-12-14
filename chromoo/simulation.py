import copy
import random
import string
import subprocess
from pathlib import Path

from chromoo.utils import keystring_todict, deep_get, sse, readChromatogram, readArray
import numpy as np
import os

from cadet import Cadet
from addict import Dict

from ruamel.yaml import YAML

def load_file(fname):
    yaml=YAML(typ='safe')
    yaml.default_flow_style=False
    ext = Path(fname).suffix

    if ext == ".h5":
        simulation = loadh5(fname)
    elif ext == ".yaml" or ext == ".yml" :
        simulation = Cadet()
        cadetpath = subprocess.run(['which', 'cadet-cli'], capture_output=True, text=True ).stdout.strip()
        Cadet.cadet_path = cadetpath
        simulation.filename = fname.replace(ext, '.h5')
        simulation.root = Dict(yaml.load(Path(fname)))
    else:
        raise(RuntimeError('Invalid simulation file!'))

    return simulation


def loadh5(filename):
    """
        Load a cadet simulation file
    """

    cadetpath = subprocess.run(['which', 'cadet-cli'], capture_output=True, text=True ).stdout.strip()
    Cadet.cadet_path = cadetpath

    sim = Cadet()
    sim.filename = filename
    sim.load()

    return sim

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
    # FIXME: only objectives[0] is checked
    
    objectives_contain_times = True
    if objectives[0].times:
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
        cur_len = p.length

        if p.type == 'element' :
            arr = sim.root
            for key in p.path.split('.'):
                arr = arr[key]
            value = x[prev_len : prev_len + cur_len]
            arr[p.index] = value
            cur_dict = keystring_todict(p.path, arr)
        else:
            cur_dict = keystring_todict(p.path, x[prev_len : prev_len + cur_len])

        sim.root.update(cur_dict)
        prev_len += p.length
