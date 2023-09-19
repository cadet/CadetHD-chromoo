# ChroMOO (or chromoo)

Chromatography optimization with cadet and pymoo. I built this because CADET-Match didn't offer optimization with certain parameters and objectives. For example, optimizing SOLUTION_BULK is not possible currently. Input of vector parameters is also currently not possible.

While I haven't yet fully looked through the source code of CADET-Match, I would like to take inspiration from it while building chromoo. Eventually, when I get a better understanding of pymoo, CADET-Match and the problem, I believe it should be possible to merge the code into CADET-Match.

# Installation

```
pip install .
```

# Usage

Chromoo requires a YAML config file. I use ruamel.yaml, which allows using YAML v1.2, meaning comments are allowed, and exponential notation is better parsed.

A template of the config follows:

```yaml
filename: 10k-mono.mono1d.h5
load_checkpoint: checkpoint.npy
force_checkpoint_continue: false
nproc: 4
store_temp: false
transforms: 
  parameters: lognorm
  objectives: geometric
parameters:
    - name: axial
      length: 1
      path: input.model.unit_002.col_dispersion
      min_value: 1.0e-9
      max_value: 1.0e-4
objectives: 
    - name: outlet
      filename: chromatogram-from-xns.csv
      # times: timesteps.txt
      score: sse
      path: output.solution.unit_003.solution_outlet_comp_000
algorithm: 
  name: nsga3
  pop_size: 10
termination:
  x_tol: 1e-8
  cv_tol: 1e-6
  f_tol: 1e-9
  nth_gen: 2
  n_last: 10
  n_max_gen: 10
  n_max_evals: 100000
```

# Notes
- It runs multiple cadet simulations from a pool size of `nproc` for every evaluation of a population.
- parameters and objectives are **lists**
- Objective targets can be provided as an (times,values) csv file in `objectives.filename` or with the times separately specified in `objectives.times`
    - chromatograms already contain times, so it's easier to just provide the filename
    - solution_bulk data obtained from 3D sims are multidimensional, and we would like to try fitting the whole thing as a flat vector first
- The `solution_times` section of the provided cadet simulation will be changed to match those of `objectives[0]` exactly.
- Recommended population sizes for n-dimensional problems is 100*n
- [CRIT] Don't fit porosity and velocity together. You can fit porosity and flowrate instead
- Provided examples, while valid, are *NOT* guaranteed to be correct. Though I will try to keep them correct. 
- Checkpoints are saved at every generation by default. Checkpoints help avoid the pain of libpthread (or other) crashes from having to completely restart the fitting.
- Use `force_checkpoint_continue` to force the algorithm to continue from a terminated checkpoint. Helpful if you made the termination criteria stricter.
- Be careful when resuming from a checkpoint. Any changes to problem parameters might not be reflected because the algorithm/problem is fully restored from the checkpoint
- `transforms.parameters` (choices = [`lognorm`, `norm`, `none`]) applies to all inputs individually
- `transforms.objectives` (choices = [`none`, `mean`, `geometric`]) will be made to convert multiple objectives into a single objective.

# Known Issues
- [CRIT] Got simulation failure due to `error 4 in libpthread` (see dmesg when it happens) on IBT012. Simulation runs manually.
- Reading inputs from YAML loads strings as `str` and from h5 files we get `numpy.bytes_`. CADET-Python run_load() uses load_results() instead of full load(). So if we check for input string values after simulation, the type of it depends on whether we use full load() or load_results() since we deal with YAML files as well. So we have to consider whether we deal with strings or bytestrings. Simple solution: Don't use run_load in scripts.
- Loading checkpoints also loads the previous values for all/most parameters. So if nproc is updated before loading, the new value isn't used.

# TODO
- [ONGO] Move to numpy arrays
- [CRIT] Hypervolume indicator as a convergence criterion
- [DONE] Replace readArray, readChromatogram with np.genfromtxt or loadtxt
- [DONE] Implement Objective vs Objective 2D plots
- [TASK] Adjust Verbose Display according to algorithm used
- [TASK] Random seeds
- [TASK] Make sure tests delete temp files
- [TASK] Write unit tests for all classes
- [TASK] Write a configHandler method to output a dummy config.
- [CRIT] For the split-chromatogram problem, we know that the axial dispersion in once radial shell won't affect the chromatogram in another, so it does have a constraint. Is there a way to constrain the parameters that way? Or does it just mean we solve the system serially? 
- [TASK] Unified interface/method for deep getting and setting from/to a Dict or dict
- [TASK] Fix typings for configHandler attributes
- [DONE] Pickle pop xs and fs for use with chromoo-post
- [TASK] Own pareto front
- [TASK] chromoo-post: plots
    - [DONE] objectives vs objectives: corner
    - [DONE] ALL parameters_objectives plots (as subplots and separate)
    - [TASK] Best per generation (opts)
    - [TASK] Best per generation (pops)
    - [TASK] Best ever
- [TASK] Consider weighting objectives: Look at weighted least squares
- [TASK] Consider multi-started/restarted systems
- [TASK] Check out numpickle: https://gwang-jin-kim.medium.com/faster-loading-and-saving-of-pandas-data-frames-using-numpickle-numpy-and-pickle-d15870519529
- Performance of np.take() with numbajit vs boolean indexing: https://stackoverflow.com/questions/46041811/performance-of-various-numpy-fancy-indexing-methods-also-with-numba
- Improved plotting for large number of subplots in post: https://stackoverflow.com/questions/13046127/matplotlib-very-slow-is-it-normal/13060980#13060980
- [CRIT] Check for behavior when take=[2,[0,1,2...]]. i.e., when indices is a list. Does verify fail? What happens?
