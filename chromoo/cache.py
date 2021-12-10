from operator import itemgetter

from chromoo.plotter import Plotter, Subplotter
import numpy as np

class Cache:
    """
        Should store problem data
    """
    def __init__(self, parameters, objectives, simulation, filename='cache.csv') -> None:

        self.database = []          # n_generation x n_individual x [n_par + n_obj]
        self.best_scores = []
        self.last_best_individual = []

        self.parameters = parameters
        self.objectives = objectives
        self.n_par = sum( p.length for p in parameters )
        self.n_obj = len(objectives)
        self.filename = filename

        self.simulation = simulation

    def add(self, population:list, scores:list) -> None:
        self.database.append(np.column_stack((population, scores)))

    def best_gen(self, igen:int):
        return min(self.database[igen], key=itemgetter(1))

    def worst_gen(self, igen:int):
        return max(self.database[igen], key=itemgetter(1))

    def best_all(self):
        return min(self.best_gen(i)[1][0] for i,_ in enumerate(self.database))

    def best_all_slice(self, index:int):
        return min(self.best_gen(i)[1][0] for i,_ in enumerate(self.database[0:index]))

    def scatter_gen(self, igen:int, 
        title=None,
        xscale='linear', 
        yscale='linear'
    ) -> None:
        """ Write a scatterplot for the i'th generation """

        arr = np.array(self.database)

        for i_obj in range(self.n_obj):
            for i_par in range(self.n_par):
                x = arr[igen,:,i_par]
                y = arr[igen,:,self.n_par + i_obj]

                plot = Plotter(
                    title=title,
                    xlabel= f"{i_par}",
                    ylabel= f"{i_obj}",
                    xscale=xscale,
                    yscale=yscale
                )

                plot.scatter(x,y)
                plot.save(f"gen{igen}_{i_par}_{i_obj}.pdf")

    def scatter_all(self,
        title=None,
        xscale='linear', 
        yscale='linear'
    ) -> None:
        """ Write a scatterplot for all generations """

        arr = np.array(self.database)

        plot = Subplotter(
            nrows=self.n_obj,
            ncols=self.n_par,
            title=title,
            xscale=xscale,
            yscale=yscale
        )

        for i_obj in range(self.n_obj):
            for i_par in range(self.n_par):
                x = arr[:,:,i_par]
                y = arr[:,:,self.n_par + i_obj]

                plot.scatter(x,y, i_obj,i_par, xlabel=f"{i_par}", ylabel=f"{i_obj}")

        plot.save(f"ALL.pdf")
        plot.close()

    def plot_best_scores(self):
        plot = Plotter(
            title='Best Scores', 
            xlabel='generations',
            ylabel='Score',
            yscale='log'
        )

        plot.plot(range(1,len(self.best_scores)+1), self.best_scores)
        plot.save(f"best_scores.pdf")
