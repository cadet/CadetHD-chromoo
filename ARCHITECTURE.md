# Architecture

This file provides a simple explanation for the design and purpose of Chromoo's classes and how they couple. This ends up being a description of how `pymoo` is designed, since we are necessarily restricted to implement our program under the constraints of the optimization framework.

Below, you will find a rough overview of the classes used in Chromoo, how they couple together to allow running the optimization process, and some general features of this program.

## Classes
- ChromooProblem -> pymoo.core.problem.Problem
    - has `_evaluate()` to do run simulations for every generation
- ChromooCallback -> pymoo.core.callback.Callback
    - Is run after every generation
    - Used to update cache and store population and Pareto front data
- pymoo.util.termination.default.MultiObjectiveDefaultTermination
    - Termination criteria for the optimizer
- AlgorithmFactory -> Use pymoo.{algorithms,factory,operators} 
    - Build and init an algorithm.
- CadetSimulation -> cadet.Cadet
    - Extensions of the existing `Cadet` class
    - Allow loading config as yaml
    - Methods to calculate solute mass in each domain
- Objective
    - Calculate objective scores given a completed cadet simulation
    - Can handle slicing/averaging/summing of multi-dimensional solution data
- Parameter
    - Container for a given parameter (or list)
    - Can handle scalar, vector, or element (specific indices in a vector) as parameter
- Scores
    - module to store scoring functions
    - sse, rmse, nrmse, logsse, logrmse
- Transforms
    - module to store transform (normalization) functions
    - lognorm, lognorm_inverse, normalize, denormalize, identity


## Architecture / Design / Coupling
- Algorithm setup loads the Problem, Termination criteria, Callback, and Initial Population
- Algorithms can be run step-by-step (step = generation)
- On each run, a callback can be provided to perform specific tasks after each step. 
    - We use this to save data into a pd.Dataframe via our `Cache` class
- Problems have a `_evaluate` method that does the work. It takes the parameters as an array, and returns an array of objective scores. 
    - The inputs X are provided by pymoo, and may be in the normalized space. Thus a denormalization may be required before passing them on to the actual evaluation process.
    - In our case, each individual in the given population is evaluated in its own thread (Set nthreads=1 in the cadet simulation template), and multiple evaluations can be performed in parallel.


## Features

### Fitting
- normalization of data for parameters and objectives
- sobol initialization
- restart fitting from last generation
- store population results for all generations
- store latest Pareto front

- pymoo v0.5 algorithms: UNSGA3/NSGA3

- Fit scalars, full vectors, or specific elements of vectors
- Allow slicing high-dimensional vectors to generate objectives

### Post
- Convergence plots (Metascore/objectivescores per generation)
- Response plots (Parameter vs Objective Score) 
- Performance plots (Objectives vs Reference)
- Corner plots (High dimensional views of specific dataset)
- Violin plots for parameter values in Pareto front
