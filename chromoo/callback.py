from pymoo.core.callback import Callback

from math import sqrt
import numpy as np

import csv
import os

import asyncio
from chromoo.transforms import transforms

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

        self.cache.update_database(algorithm.pop.get('X'), algorithm.pop.get('F'))
        self.cache.opt = algorithm.opt
        
        ## TODO: asyncio subprocess
        self.cache.update_scatter_plot()
        self.cache.write_pareto()

