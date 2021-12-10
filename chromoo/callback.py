from pymoo.core.callback import Callback
from chromoo.simulation import run_sim

class ChromooCallback(Callback):

    def __init__(self, cache) -> None:
        super().__init__()
        self.cache = cache
        self.data["best_scores"] = []
        self.data["last_best_individual"] = []

    def notify(self, algorithm):
        # NOTE: Only captures the first of many best solutions for MOOs
        f_opt0 = algorithm.opt[0].F
        x_opt0 = algorithm.opt[0].X

        F = algorithm.pop.get("F")
        X = algorithm.pop.get("X")

        self.data["best_scores"].append(f_opt0)
        self.data["last_best_individual"] = x_opt0
        self.update_cache(X, F)
        self.save_last_best()

    def update_cache(self, X, F):
        self.cache.add(X,F)
        self.cache.scatter_all(
            title=f"gen_all",
            xscale='log',
            yscale='log',
        )

        self.cache.best_scores = self.data["best_scores"]
        self.cache.plot_best_scores()
        self.cache.last_best_individual = self.data["last_best_individual"]

    def save_last_best(self):
        run_sim(self.data["last_best_individual"], self.cache.simulation, self.cache.parameters, "last_best.h5", store=True)
