from chromoo.plotter import Plotter, Subplotter
import numpy as np
from chromoo.transforms import transform_array

import csv
import os

class Cache:
    """
        Should store problem data
    """
    def __init__(self, config) -> None:

        self.pop_Xs = []
        self.pop_Fs = []

        self.opt_Xs = []
        self.opt_Fs = []

        self.best_combined_per_gen = []
        self.best_combined_ever = []

        self.parameters = config.parameters
        self.objectives = config.objectives

        self.parameter_transform = config.parameter_transform
        # self.objective_transform = config.objective_transform

        self.n_par = config.n_par
        self.n_obj = config.n_obj

        self.parameter_names = config.parameter_names 
        self.objective_names = config.objective_names 

        self.par_min_values = config.par_min_values
        self.par_max_values = config.par_max_values

        self.simulation = config.simulation

    def update(self, algorithm):
        """ Inverse transform the algorithm pop and opt and save them """

        self.pop_Xs.append(transform_array(algorithm.pop.get('X'), self.par_min_values, self.par_max_values, self.parameter_transform, mode='inverse'))
        self.opt_Xs.append(transform_array(algorithm.opt.get('X'), self.par_min_values, self.par_max_values, self.parameter_transform, mode='inverse'))

        self.pop_Fs.append(algorithm.pop.get('F'))
        self.opt_Fs.append(algorithm.opt.get('F'))

        self.update_best_scores()

        # self.pops.append(transform_population(algorithm.pop, self.par_min_values, self.par_max_values, self.parameter_transform, 'inverse'))
        # self.opts.append(transform_population(algorithm.opt, self.par_min_values, self.par_max_values, self.parameter_transform, 'inverse'))
    #
    
    def initialize(self):
        try: 
            os.remove('opts.csv')
        except FileNotFoundError:
            pass

        try: 
            os.remove('best_combined_per_gen.csv')
        except FileNotFoundError:
            pass

    
    def scatter_gen(self, igen:int, 
        title=None,
        xscale='linear', 
        yscale='linear'
    ) -> None:
        """ Write a scatterplot for the i'th generation """

        arrx = np.array(self.pop_Xs)
        arry = np.array(self.pop_Fs)

        for i_obj in range(self.n_obj):
            for i_par in range(self.n_par):
                x = arrx[igen,:,i_par]
                y = arry[igen,:,i_obj]

                plot = Plotter(
                    title=title,
                    xlabel= f"{i_par}",
                    ylabel= f"{i_obj}",
                    xscale=xscale,
                    yscale=yscale
                )

                plot.scatter(x,y)
                plot.save(f"gen{igen}_{self.parameter_names[i_par]}_{self.objective_names[i_obj]}.png")
                plot.close()

    def scatter_all(self,
        title=None,
        xscale='linear', 
        yscale='linear'
    ) -> None:
        """ Write a scatterplot for all generations """

        plot = Subplotter(
            nrows=self.n_obj,
            ncols=self.n_par,
            title=title,
            xscale=xscale,
            yscale=yscale
        )

        arrx = np.array(self.pop_Xs)
        arry = np.array(self.pop_Fs)

        for i_obj in range(self.n_obj):
            for i_par in range(self.n_par):
                x = arrx[:,:,i_par]
                y = arry[:,:,i_obj]

                plot.scatter(x,y, i_obj,i_par, xlabel=self.parameter_names[i_par], ylabel=self.objective_names[i_obj])

        plot.save(f"ALL.png")
        plot.close()

    def write_opts(self):
        """ Write the last generation's opts solution to a csv file """
        # TODO: Use pandas or something
        with open('opts.csv', 'w') as fp:
            writer = csv.writer(fp)
            writer.writerow(self.parameter_names + self.objective_names)
            writer.writerows(map(lambda x,f: np.append(x,f) , self.opt_Xs[-1], self.opt_Fs[-1]))

    def write_best_combined_per_gen(self):
        """ Write to CSV the best combined score per generation """
        with open('best_combined_per_gen.csv', 'a') as fp:
            writer = csv.writer(fp)
            writer.writerow([self.best_combined_per_gen[-1]])

    def write(self):
        self.write_opts()
        self.write_best_combined_per_gen()

    def update_scatter_plot(self):
        """ Update the objectives_vs_parameters scatter plots """
        self.scatter_all(
            title=f"gen_all",
            xscale='log',
            yscale='log',
        )

    def find_best_score(self, method='geometric', generation_index=-1):
        """ Find the best solution in the opts set """
        if method == 'geometric':
            means = np.fromiter(map(lambda f: np.array(f).prod()**(1.0/len(f)) , self.opt_Fs[generation_index]), float)
            min_index = np.argmin(means)
        else: 
            raise RuntimeError("Invalid method to find best solution!")

        return min_index, means

    def update_best_scores(self):
        index,means = self.find_best_score(generation_index=-1)

        self.best_combined_per_gen.append(means[index])
        self.best_combined_ever.append(np.min(self.best_combined_per_gen))

    def plot_best_scores(self):
        plot_best_generational = Plotter(
            title='Best Geometric Mean Per Generation',
            xlabel='Generation',
            ylabel='Mean score',
            xscale='linear',
            yscale='log'
        )

        plot_best_generational.plot(range(1,len(self.best_combined_per_gen)+1), self.best_combined_per_gen)
        plot_best_generational.save('best_combined_per_gen.png')
        plot_best_generational.close()

        plot_best_ever = Plotter(
            title='Best Geometric Mean Ever',
            xlabel='Generation',
            ylabel='Mean score',
            xscale='linear',
            yscale='log'
        )

        plot_best_ever.plot(range(1,len(self.best_combined_ever)+1), self.best_combined_ever)
        plot_best_ever.save('best_combined_ever.png')
        plot_best_ever.close()
