from pymoo.core.problem import Problem
from itertools import chain
from functools import partial

import multiprocessing as mp
from pathlib import Path
from chromoo.simulation import run_and_eval
from chromoo.transforms import transform_array

from chromoo.cadetSimulation import new_run_and_eval

class ChromooProblem(Problem):
    def __init__(self, sim, parameters, objectives, nproc=4, tempdir='temp', store_temp=False, transform='none'):
        
        self.min_values = []
        self.max_values = []

        # chaining min and max values
        for p in parameters:
            self.min_values = list(chain(self.min_values, p.min_value))
            self.max_values = list(chain(self.max_values, p.max_value))

        n_var = sum(p.length for p in parameters)

        self.transform = transform

        if self.transform != 'none':
            xls = [0] * n_var
            xus = [1] * n_var
        else: 
            xls = self.min_values
            xus = self.max_values

        super().__init__(
            n_var = n_var,
            n_obj = sum(o.n_obj for o in objectives), 
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
            denormalized_inputs = transform_array(X, self.min_values, self.max_values, self.transform, mode='inverse')
            out["F"] = pool.map( 
                    partial(
                        new_run_and_eval, 
                        sim=self.sim, 
                        parameters=self.parameters, 
                        objectives=self.objectives, 
                        name=None, 
                        tempdir=self.tempdir, 
                        store=self.store_temp), 
                    denormalized_inputs)
