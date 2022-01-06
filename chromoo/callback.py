from pymoo.core.callback import Callback

import asyncio

class ChromooCallback(Callback):

    def __init__(self, cache) -> None:
        super().__init__()
        self.cache = cache

        self.cache.initialize()

    def notify(self, algorithm):
        """ Main callback method """

        ## TODO: asyncio subprocess
        self.cache.update(algorithm)

        asyncio.run(self.subcallback())

    async def subcallback(self):
        await asyncio.gather(
            asyncio.to_thread(self.cache.write),
            asyncio.to_thread(self.cache.update_scatter_plot),
            asyncio.to_thread(self.cache.plot_best_scores)
        )
