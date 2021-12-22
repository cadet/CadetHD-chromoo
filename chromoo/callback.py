from pymoo.core.callback import Callback
from chromoo.simulation import run_sim

from math import sqrt
import numpy as np

import csv
import os

import asyncio

class ChromooCallback(Callback):

    def __init__(self, cache) -> None:
        super().__init__()
        self.cache = cache

        try: 
            os.remove('pareto.csv')
        except FileNotFoundError:
            pass

    def notify(self, algorithm):
        self.algorithm = algorithm
        asyncio.run(self.subcallback())

    async def subcallback(self):
        await asyncio.gather(
            asyncio.to_thread(self.save_last_best),
            asyncio.to_thread(self.plot_best_scores),
            asyncio.to_thread(self.plot_best_score_magnitude),
            asyncio.to_thread(self.update_scatter_plot),
            asyncio.to_thread(self.write_pareto)
        )


    def update_scatter_plot(self):
        F = self.algorithm.pop.get("F")
        X = self.algorithm.pop.get("X")
        self.cache.add(X,F)
        self.cache.scatter_all(
            title=f"gen_all",
            xscale='log',
            yscale='log',
        )

    def save_last_best(self):
        x_opt0 = self.algorithm.opt[0].X
        self.cache.last_best_individual = x_opt0
        run_sim(self.cache.last_best_individual, self.cache.simulation, self.cache.parameters, "last_best.h5", store=True)

    def plot_best_scores(self):
        f_opt0 = self.algorithm.opt[0].F
        self.cache.best_scores.append(f_opt0)
        self.cache.plot_best_scores()

    def plot_best_score_magnitude(self):
        opt = self.algorithm.opt
        obj_magnitudes = self.magnitude(opt)
        best_score_magnitude = obj_magnitudes[0]
        self.cache.best_score_magnitude_pareto0.append(best_score_magnitude)
        self.cache.plot_best_score_magnitude()

    def magnitude(self, algo_opts):
        """ return magnitudes of a list of vectors """
        return [ sqrt(sum(map(lambda x: x**2, opt.F))) for opt in algo_opts ]

    def write_pareto(self):
        with open('pareto.csv', 'w') as fp:
            writer = csv.writer(fp)
            writer.writerow(self.cache.p_names + self.cache.o_names)
            writer.writerows(map(lambda opt: np.append(opt.X, opt.F) , self.algorithm.opt))
