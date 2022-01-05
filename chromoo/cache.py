from chromoo.plotter import Plotter, Subplotter
import numpy as np
from chromoo.transforms import transform_population, transforms
from itertools import chain

import csv

class Cache:
    """
        Should store problem data
    """
    def __init__(self, config) -> None:

        # Database of all populations for all generations and their results
        self.database = []          # n_generation x n_individual x [n_par + n_obj]

        # algorithm.opt for the latest generation
        self.opt = None

        self.parameters = config.parameters
        self.objectives = config.objectives

        self.parameter_transform = config.parameter_transform
        self.objective_transform = config.objective_transform

        self.n_par = sum( p.length for p in config.parameters )
        self.n_obj = len(config.objectives)

        self.p_names = []
        self.o_names = []

        for p in self.parameters:
            for i in range(p.length):
                self.p_names.append(f"{p.name}[{i}]")

        for o in self.objectives:
            self.o_names.append(f"{o.name}")
            
        self.par_min_values = config.par_min_values
        self.par_max_values = config.par_max_values

        self.simulation = config.simulation

    def update_database(self, population:list, scores:list) -> None:
        denormalized_population = transform_population(population, self.par_min_values, self.par_max_values, self.parameter_transform, mode='inverse')
        self.database.append(np.column_stack((denormalized_population, scores)))

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
                plot.save(f"gen{igen}_{self.p_names[i_par]}_{self.o_names[i_obj]}.png")
                plot.close()

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

                plot.scatter(x,y, i_obj,i_par, xlabel=self.p_names[i_par], ylabel=self.o_names[i_obj])

        plot.save(f"ALL.png")
        plot.close()

    def write_pareto(self):
        """ Write the current Pareto solution to a csv file """
        # TODO: Use pandas or something
        with open('pareto.csv', 'w') as fp:
            writer = csv.writer(fp)
            writer.writerow(self.p_names + self.o_names)
            writer.writerows(map(lambda opt: np.append(transforms[self.parameter_transform]['inverse'](opt.X, self.par_min_values, self.par_max_values), opt.F) , self.opt))

    def update_scatter_plot(self):
        """ Update the objectives_vs_parameters scatter plots """
        self.scatter_all(
            title=f"gen_all",
            xscale='log',
            yscale='log',
        )
