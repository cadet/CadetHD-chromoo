#!/usr/bin/env python3

from pathlib import Path
from chromoo.plotter import Plotter, Subplotter
from chromoo.cadetSimulation import run_iter
import numpy as np
import pandas as pd
from scipy import stats
import multiprocessing as mp
from functools import partial

from matplotlib import pyplot as plt
import matplotlib as mpl 
import matplotlib.cm as cm
import os

from joblib import Parallel, delayed, Memory

# TODO: Corner plots (see seaborn for ideas instead of corner.py)

mpl.use('Agg')

pd.set_option('display.float_format', lambda x: '%e' % x)
pd.set_option('display.max_columns', None)

def violin(dataframe, percentile:int=100, postdir=Path('post'), name='violin'): 
    """
    Generate violin plots of all optimal parameters, joined by lines
    """
    # cmapname = 'YlOrRd'
    # npoints = len(best_pars_reversed)
    cmapname = 'tab10'
    npoints = 1
    n_par = dataframe.columns.size

    nrows = int(percentile / 100 * dataframe.shape[0])
    dataframe = dataframe.head(nrows)

    with Plotter(f'Parameter values (n={nrows}, {percentile}%)', cmap=cmapname, n_total_curves=npoints, yscale='log') as vplot: 
        violin_parts = vplot.ax.violinplot(dataset = list(dataframe.to_numpy().T), positions=range(n_par))
        for pc in violin_parts['bodies']:
            pc.set_facecolor(vplot.colors[0])
            pc.set_edgecolor('black')
            pc.set_alpha(1.0)
        for partname in ('cbars','cmins','cmaxes'):
            vp = violin_parts[partname]
            vp.set_edgecolor('black')
            vp.set_linewidth(1)
        # for i in range(npoints): 
        #     vplot.scatter(range(n_par), dataframe.to_numpy()[i], s=4 )
        vplot.ax.set_xticks(range(n_par))
        vplot.ax.set_xticklabels(dataframe.columns, rotation=45, ha='right')
        vplot.ax.minorticks_off()
        vplot.save(postdir / name , dpi=300)

def response_surface(populations, config, postdir=Path('post'), filename=f"response_surface_2D", opts=None):

    plot = Subplotter(
        nrows=len(config.objective_names),
        ncols=len(config.parameter_names),
        title='',
        xscale='log',
        yscale='log'
    )

    try:
        gens = populations['generation'].to_numpy()
    except KeyError: 
        gens = np.array([1])
    nmax = max(gens)

    # https://stackoverflow.com/questions/30108372/how-to-make-matplotlib-scatterplots-transparent-as-a-group

    for i_obj, obj in enumerate(config.objective_names): 
        for i_par, par in enumerate(config.parameter_names): 

            x = populations[par]
            y = populations[obj]

            plot.scatter( 
                x,y, 
                i_obj, i_par, 
                xlabel=f'{config.parameter_names[i_par]}',
                ylabel=f'{config.objective_names[i_obj]}',
                fontsize=7, s=8, c='gray', lw=0, alpha=0.5,
                # title=f'{parameter_names[i_par]} v {objective_names[i_obj]}',
            )

            if opts is not None:
                plot.scatter( 
                    opts[par], opts[obj],
                    i_obj, i_par, 
                    xlabel=f'{config.parameter_names[i_par]}',
                    ylabel=f'{config.objective_names[i_obj]}',
                    fontsize=7, s=8, lw=0, c='red'
                    # title=f'{parameter_names[i_par]} v {objective_names[i_obj]}',
                )
            else:
                plot.scatter( 
                    populations[populations['generation']==nmax][par],
                    populations[populations['generation']==nmax][obj], 
                    i_obj, i_par, 
                    xlabel=f'{config.parameter_names[i_par]}',
                    ylabel=f'{config.objective_names[i_obj]}',
                    fontsize=7, s=8, lw=0, c='red',
                    # title=f'{parameter_names[i_par]} v {objective_names[i_obj]}',
                )

    plot.save(postdir / filename, dpi=300)
    plot.close()

def response_surface_split(populations, config, postdir=Path('post'), name=f"response_surface_2D"):
    try:
        gens = populations['generation'].to_numpy()
    except KeyError: 
        gens = np.array([1])
    nmax = max(gens)

    for i_obj, obj in enumerate(config.objective_names): 
        for i_par, par in enumerate(config.parameter_names): 
            plot = Plotter(title=f"{par} vs {obj}", xlabel=f"{par}", ylabel=f"{obj}", xscale='log', yscale='log')
            x = populations[par]
            y = populations[obj]

            plot.scatter(x,y, c='gray', alpha=0.5, lw=0)

            plot.scatter(
                populations[populations['generation']==nmax][par],
                populations[populations['generation']==nmax][obj], 
                c='red', lw=0
            )

            plot.save(postdir / f"{name}_{obj}_{par}", dpi=300)
            plot.close()

def convergence(populations, column, postdir=Path('post'), name='convergence'):
    # minned = populations.loc[populations.groupby(['generation'])[args.mean].idxmin()]
    labels=['min', 'median', 'max']
    best_per_gen = populations.groupby(['generation'])[column].min()
    median_per_gen = populations.groupby(['generation'])[column].median()
    worst_per_gen = populations.groupby(['generation'])[column].max()

    plot = Plotter(title=f'Convergence', yscale='log', xlabel='Generations', ylabel=column)
    plot.plot(range(len(best_per_gen)), best_per_gen, label=labels[0])
    plot.plot(range(len(median_per_gen)), median_per_gen, label=labels[1])
    plot.plot(range(len(worst_per_gen)), worst_per_gen, label=labels[2])
    plot.legend('upper right', (1,1))
    plot.save(postdir / name, dpi=300)
    plot.close()

    # populations_best_score_ever_index = populations[args.mean].argmin()
    # print(populations.iloc[populations_best_score_ever_index])

def load_dataframe_sort(filename, columns_to_mean, sort_by=None):
    if Path(filename).suffix == '.csv':
        df = pd.read_csv(filename)
    else:
        df = pd.read_pickle(filename)
        df = df.apply(pd.to_numeric)

    df['geometric'] = stats.gmean(df[columns_to_mean], axis=1)
    df['arithmetic'] = df[columns_to_mean].mean(axis=1)
    df['rms'] = np.sqrt(np.square(df[columns_to_mean]).mean(axis=1)) 

    if sort_by:
        df = df.sort_values(by=[sort_by])

    # df.to_csv(postdir / f"opts_{args.mean}.csv")
    return df

memory = Memory('./cache', verbose=0)
run_iter_cached = memory.cache(run_iter)

def run_sims_parallel(dataframe, config, nproc=os.cpu_count(), postdir=Path('post'), suffix=None):
    sims = Parallel(n_jobs=nproc)(
        delayed( 
            partial(run_iter_cached, 
                    sim=config.simulation, 
                    parameters=config.parameters, 
                    objectives=config.objectives,
                    name=f'sim_{suffix}', 
                    tempdir=postdir, 
                    store=True)
        )
        (x) for x in enumerate(dataframe[dataframe.columns[0:config.n_par]].values)
    )

    # with mp.Pool(nproc) as pool:
    #     sims = pool.map( 
    #         partial(run_iter, 
    #                 sim=config.simulation, 
    #                 parameters=config.parameters, 
    #                 objectives=config.objectives,
    #                 name=f'sim_{suffix}', 
    #                 tempdir=postdir, 
    #                 store=True), 
    #         enumerate(dataframe[dataframe.columns[0:config.n_par]].values))

    return sims

def performance_range_split(sims, config, postdir=Path('post'), suffix=None):
        list_integrals_all_sims= []

        for i,sim in enumerate(sims):
            list_integrals_all_sims.append(list(map(lambda obj: obj.integral(sim) ,config.objectives)))

        idx_max_integrals = np.argmax(list_integrals_all_sims, axis=0).flatten()
        idx_min_integrals = np.argmin(list_integrals_all_sims, axis=0).flatten()

        for i, obj in enumerate(config.objectives):
            t, split_y_max = obj.xy(sims[idx_max_integrals[i]])
            t, split_y_min = obj.xy(sims[idx_min_integrals[i]])

            performance_comparison_range =  Plotter(title=None, cmap='tab10', xlabel='Time', ylabel='concentration') 

            label_prefix = f'{obj.name}'
            for j in range(obj.n_obj): 
                label = label_prefix if obj.n_obj == 1 else f'{label_prefix}[{j}]'
                performance_comparison_range.ax.fill_between(t, split_y_max[j], split_y_min[j], interpolate=True, alpha=0.5)

            performance_comparison_range.ax.plot(obj.x0, obj.y0, ls='dashdot', label=[f'{obj.name}[{j}] ref' for j in range(obj.n_obj)])


            plt.legend()
            performance_comparison_range.save(f"{str(postdir)}/performance_range_{obj.name}", dpi=300)
            performance_comparison_range.close()

def performance_range(sims, config, postdir=Path('post'), suffix=None):
        performance_comparison_range =  Plotter(title=None, cmap='tab10', xlabel='Time', ylabel='concentration') 
        list_integrals_all_sims= []

        for i,sim in enumerate(sims):
            list_integrals_all_sims.append(list(map(lambda obj: obj.integral(sim) ,config.objectives)))

        idx_max_integrals = np.argmax(list_integrals_all_sims, axis=0).flatten()
        idx_min_integrals = np.argmin(list_integrals_all_sims, axis=0).flatten()

        for i, obj in enumerate(config.objectives):
            t, split_y_max = obj.xy(sims[idx_max_integrals[i]])
            t, split_y_min = obj.xy(sims[idx_min_integrals[i]])

            label_prefix = f'{obj.name}'
            for j in range(obj.n_obj): 
                label = label_prefix if obj.n_obj == 1 else f'{label_prefix}[{j}]'
                performance_comparison_range.ax.fill_between(t, split_y_max[j], split_y_min[j], interpolate=True)
            # TODO: Add reference curve

        performance_comparison_range.save(f"{str(postdir)}/performance_range", dpi=300)
        performance_comparison_range.close()

def performance_combined(sims, config, postdir=Path('post'), suffix=None):
    for index,sim in enumerate(sims):
        with Plotter(title=None, cmap='tab20', xlabel='Time', ylabel='Normalized concentration') as obj_ref_plot: 
            for obj in config.objectives:
                obj.plot(sim, obj_ref_plot.ax)
            obj_ref_plot.ax.legend(loc='best')
            obj_ref_plot.save(f"{str(postdir)}/performance_combined_{index:03d}_{suffix}", dpi=300)

def performance_split(sims, config, postdir=Path('post'), suffix=None):
    for index,sim in enumerate(sims):
        for obj in config.objectives:
            with Plotter(title=f'{obj.name}', cmap='tab20', xlabel='Time', ylabel='') as obj_ref_plot: 
                obj.plot(sim, obj_ref_plot.ax)
                obj_ref_plot.ax.legend(loc='best')
                obj_ref_plot.save(f"{str(postdir)}/performance_{index:03d}_{obj.name}_{suffix}", dpi=300)

def write_objectives(sims, config, postdir=Path('post'), suffix=None):
    for index, sim in enumerate(sims):
        for obj in config.objectives:
            obj.to_csv(sim, f'{postdir.as_posix()}/sim_{index:03d}_{suffix}.csv')

    # TODO: Add headers to csv
    for obj in config.objectives:
        obj.ref_to_csv(f'{postdir.as_posix()}/ref.csv')
