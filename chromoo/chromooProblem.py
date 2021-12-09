from pymoo.core.problem import Problem
from itertools import chain
from functools import partial
import multiprocessing as mp

import copy
import string
import random

from chromoo.utils import keystring_todict, deep_get, sse, readChromatogram, readArray

from chromoo.cache import Cache

import numpy as np
from pathlib import Path
import subprocess

import os

class ChromooProblem(Problem):
    def __init__(self, sim, parameters, objectives, nproc=4, tempdir='temp', store_temp=False):
        
        xls = []
        xus = []

        # NOTE: Scalars are autoconverted to lists and chained
        for p in parameters:
            if isinstance(p.min_value, float):
                p.min_value = [p.min_value] * p.length
            if isinstance(p.max_value, float):
                p.max_value = [p.max_value] * p.length

            xls = list(chain(xls, p.min_value))
            xus = list(chain(xus, p.max_value))

        super().__init__(
            n_var = sum(p.get('length') for p in parameters), 
            n_obj = len(objectives), 
            n_constr=0, 
            xl=xls,
            xu=xus )

        self.sim = sim
        self.parameters = parameters
        self.objectives = objectives
        self.nproc = nproc
        self.store_temp = store_temp

        self.tempdir=Path(tempdir)
        self.tempdir.mkdir(exist_ok=True)

        self.cache = Cache(parameters, objectives)

    def _evaluate(self, x, out, *args, **kwargs):

        with mp.Pool(self.nproc) as pool:
            # out["F"] = pool.map(self.evaluate_sim, x)
            # out["F"] = pool.starmap(self.evaluate_sim, zip(x, repeat(None), repeat(self.store_temp))
            out["F"] = pool.map(partial(self.evaluate_sim, store=self.store_temp), x)

        self.cache.add(x, out["F"])
        self.cache.scatter_all(
            title=f"gen_all",
            xscale='log',
            yscale='log',
        )

        self.cache.best_scores = kwargs.get('algorithm').callback.data["best_scores"]
        self.cache.plot_best_scores()


    def evaluate_sim(self, x, name=None, store=False):
        """
            - run one simulation
            - calculate and return scores
        """
        newsim = copy.deepcopy(self.sim)

        if name:
            newsim.filename = name
        else:
            newsim.filename = self.tempdir.joinpath('temp' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6)) + '.h5')

        self.update_sim_parameters(newsim, x)

        newsim.save()

        try:
            newsim.run(check=True)
        except subprocess.CalledProcessError as error:
            print(f"{newsim.filename} failed: {error.stderr.decode('utf-8')}")
            raise(RuntimeError("Simulation Failure"))

        newsim.load()

        sses = []

        # FIXME: Make generic scores
        
        objectives_contain_times = True
        if self.objectives[0].get('times'):
            objectives_contain_times = False

        for obj in self.objectives:
            y = deep_get(newsim.root, obj.path)
            y = np.array(y).flatten()
            if objectives_contain_times:
                _, y0 = readChromatogram(obj.filename)
            else:
                y0 = readArray(obj.filename)

            sses.append(sse(y0, y))

        if not store:
            os.remove(newsim.filename)

        return sses

    def update_sim_parameters(self, sim, x):
        # For every parameter, generate a dictionary based on the path, and
        # update the simulation in a nested way
        # TODO: Probably a neater way to do this
        prev_len = 0
        for p in self.parameters:
            cur_len = p.get('length')
            cur_dict = keystring_todict(p.get('path'), x[prev_len : prev_len + cur_len])
            sim.root.update(cur_dict)
            prev_len += p.get('length')

