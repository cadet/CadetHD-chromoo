from operator import itemgetter
from itertools import chain

from chromoo.plotter import Plotter

class Cache:
    """
        Should store problem data
    """
    def __init__(self, parameters, objectives, filename='cache.csv') -> None:

        # Database is a list of tuples([n_par], [n_obj])
        # TODO: might be better to have it as an np.ndarray to have reshapability, sliceability, and operability
        self.database = []          # n_generation x n_individual of ([n_par], [n_obj])

        self.parameters = parameters
        self.objectives = objectives
        self.n_par = sum( p.length for p in parameters )
        self.n_obj = len(objectives)
        self.filename = filename

    def add(self, population:list, scores:list) -> None:
        self.database.append(list(zip(population, scores)))

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

        for i_obj in range(self.n_obj):
            for i_par in range(self.n_par):

                x = list(map(lambda x: x[0][i_par], self.database[igen]))
                y = list(map(lambda y: y[1][i_obj], self.database[igen]))

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

        for i_obj in range(self.n_obj):
            for i_par in range(self.n_par):
                x = []
                y = []
                for generation in self.database:
                    x = chain(x, map(lambda x: x[0][i_par], generation))
                    y = chain(y, map(lambda y: y[1][i_obj], generation))

                x = list(x)
                y = list(y)

                plot = Plotter(
                    title=title,
                    xlabel= f"{i_par}",
                    ylabel= f"{i_obj}",
                    xscale=xscale,
                    yscale=yscale
                )

                plot.scatter(x,y)
                plot.save(f"ALL_{i_par}_{i_obj}.pdf")
