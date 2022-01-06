from pymoo.core.callback import Callback
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
        """ Main callback method """

        self.cache.update(algorithm)
        
        ## TODO: asyncio subprocess
        self.cache.update_scatter_plot()
        self.cache.write_pareto()
        self.cache.update_best_scores()
        self.cache.plot_best_scores()

