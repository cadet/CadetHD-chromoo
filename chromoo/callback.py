from pymoo.core.callback import Callback

class ChromooCallback(Callback):

    def __init__(self) -> None:
        super().__init__()
        self.data["best_scores"] = []

    def notify(self, algorithm):
        self.data["best_scores"].append(algorithm.pop.get("F").min())
