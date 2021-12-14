from pymoo.core.problem import Problem
from itertools import chain
from functools import partial
import multiprocessing as mp

from pathlib import Path
from chromoo.simulation import run_and_eval

class ChromooProblem(Problem):
    def __init__(self, sim, parameters, objectives, nproc=4, tempdir='temp', store_temp=False):
        
        xls = []
        xus = []

        # chaining min and max values
        for p in parameters:
            xls = list(chain(xls, p.min_value))
            xus = list(chain(xus, p.max_value))

        super().__init__(
            n_var = sum(p.length for p in parameters), 
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

    def _evaluate(self, X, out, *args, **kwargs):

        with mp.Pool(self.nproc) as pool:
            # out["F"] = pool.map(self.evaluate_sim, x)
            # out["F"] = pool.starmap(self.evaluate_sim, zip(x, repeat(None), repeat(self.store_temp))
            # out["F"] = pool.map(partial(self.evaluate_sim, store=self.store_temp), X)
            out["F"] = pool.map( partial(run_and_eval, sim=self.sim, parameters=self.parameters, objectives=self.objectives, name=None, tempdir=self.tempdir, store=self.store_temp), X)

