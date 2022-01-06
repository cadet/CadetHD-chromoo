from pymoo.core.callback import Callback


class ChromooCallback(Callback):

    def __init__(self, cache) -> None:
        super().__init__()
        self.cache = cache

        self.cache.initialize()


    def notify(self, algorithm):
        """ Main callback method """

        ## TODO: asyncio subprocess
        self.cache.update(algorithm)
        self.cache.write()

        self.cache.update_scatter_plot()
        self.cache.plot_best_scores()

