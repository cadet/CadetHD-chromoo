from pymoo.core.callback import Callback
from chromoo.simulation import run_sim

from math import sqrt
import numpy as np

import csv
import os

class ChromooCallback(Callback):

    def __init__(self, cache) -> None:
        super().__init__()
        self.cache = cache

        try: 
            os.remove('pareto.csv')
        except FileNotFoundError:
            pass

    def notify(self, algorithm):
        # NOTE: Only captures the first of many best solutions for MOOs
        f_opt0 = algorithm.opt[0].F
        x_opt0 = algorithm.opt[0].X

        F = algorithm.pop.get("F")
        X = algorithm.pop.get("X")

        best_score_magnitude = sqrt(sum(map(lambda x: x**2, algorithm.opt[0].F)))

        self.cache.best_scores.append(f_opt0)
        self.cache.best_score_magnitude_pareto0.append(best_score_magnitude)
        self.cache.last_best_individual = x_opt0

        self.update_cache(X, F)
        self.save_last_best()

        with open('pareto.csv', 'w') as fp:
            writer = csv.writer(fp)
            writer.writerow(self.cache.p_names + self.cache.o_names)
            writer.writerows(map(lambda opt: np.append(opt.X, opt.F) ,algorithm.opt))

    def update_cache(self, X, F):
        self.cache.add(X,F)
        self.cache.scatter_all(
            title=f"gen_all",
            xscale='log',
            yscale='log',
        )

        self.cache.plot_best_scores()
        self.cache.plot_best_score_magnitude()

    def save_last_best(self):
        run_sim(self.cache.last_best_individual, self.cache.simulation, self.cache.parameters, "last_best.h5", store=True)
