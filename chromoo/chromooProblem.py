from pymoo.core.problem import Problem
from itertools import chain
# from functools import partial
from multiprocessing import Pool

import copy
import string
import random

from chromoo.utils import keystring_todict, update_nested, deep_get, bin_to_arr, sse, readChromatogram, readArray

class ChromooProblem(Problem):
    def __init__(self, sim, parameters, objectives, nproc=4):
        
        super().__init__(
            n_var = sum(p.get('length') for p in parameters), 
            n_obj = len(objectives), 
            n_constr=0, 
            xl=[p.get('min_value') for p in parameters],
            xu=[p.get('max_value') for p in parameters] )  
            # xl=chain(p.get('min_value') for p in parameters),
            # xu=chain(p.get('max_value') for p in parameters) )   

        self.sim = sim
        self.parameters = parameters
        self.objectives = objectives
        self.nproc = nproc


    def _evaluate(self, x, out, *args, **kwargs):

        with Pool(self.nproc) as pool:
            out["F"] = pool.map(self.evaluate_sim, x)

    def evaluate_sim(self, x):
        """
            - run one simulation
            - calculate and return scores
        """
        newsim = copy.deepcopy(self.sim)
        newsim.filename = 'temp' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6)) + '.h5'

        # For every parameter, generate a dictionary based on the path, and
        # update the simulation in a nested way
        # TODO: Probably a neater way to do this
        prev_len = 0
        for p in self.parameters:
            cur_len = p.get('length')
            cur_dict = keystring_todict(p.get('path'), x[prev_len : prev_len + cur_len][0])
            newsim.root.update(cur_dict)
            prev_len += p.get('length')

        newsim.save()

        runout = newsim.run()
        if runout.returncode != 0:
            print(runout)
            raise RuntimeError
        newsim.load()

        sses = []

        # FIXME: Make generic scores
        # FIXME: Make generic file reading
        # FIXME: allow sse2 etc
        
        timesteps_in_file = True
        if self.objectives[0].get('timesteps'):
            timesteps_in_file = False

        for obj in self.objectives:
            y = deep_get(newsim.root, obj.get('path'))
            # y0 = bin_to_arr(obj.get('filename'), '<d')
            if timesteps_in_file:
                _, y0 = readChromatogram(obj.get('filename'))
            else:
                y0 = readArray(obj.get('filename'))

            sses.append(sse(y0, y))

        return sses
