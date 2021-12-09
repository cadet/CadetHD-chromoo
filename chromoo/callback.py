from pymoo.core.callback import Callback

class ChromooCallback(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.data["best_scores"] = []
        self.data["last_best_individual"] = []
        # self.data["best_individuals"] = []

    def notify(self, algorithm):
        last_best_score = algorithm.pop.get("F").min()
        last_best_score_index = algorithm.pop.get("F").argmin()
        last_best_individual = algorithm.pop.get("X")[last_best_score_index]
        self.data["best_scores"].append(last_best_score)
        self.data["last_best_individual"] = last_best_individual
        # self.data["best_individuals"].append(last_best_individual)
