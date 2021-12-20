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
      match_solution_times: true
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

# Known Issues
- [CRIT] Got simulation failure due to `error 4 in libpthread` (see dmesg when it happens) on IBT012. Simulation runs manually.

# TODO
- [DONE] Implement logging
- [DONE] Store outputs of every generation
- [CRIT] Corner plots, 
- [DONE] each var vs score, 
    - Make sure parameters aren't ineffective
- [DONE] Store the best simulations of the last generation
- [DONE] Check if I need to use MCMC to speed things up: No. It's used in CADET-Match for the error estimator
- [DONE] Look at pymoo.Callback
- [DONE] There's probably a neater way to reconcile using `cache`  and `ChromooCallback`
- [DONE] Look into hopsy for sampling the existing space properly: Ask Johannes, it seems like it's for constrained optimization
    - Not a great experience
    - No MOO support
- [DONE] Use subplots
- [ONGO] Move to numpy arrays
- [DONE] Allow modifying a scalar at a position inside a vector
- [DONE] Allow elements of vectors as parameters: flowrate in connections matrix.
- [DONE] Implment an own Parameter and Objective class to handle vector parameter indices easily
- [DONE] Fix plot axis labels to include parameter/objective names and indices
- [DONE] Allow YAML input along with h5
- [DONE] Implement checkpointing!
- [TASK] Last best should be a pareto front
- [TASK] Implement Objective vs Objective 2D plots
- [TASK] Write csv of all simulated points to be able to generate plots at will
- [TASK] Output results into a subdirectory to avoid polluting root
- [TASK] Implement sobolGenerations
- [TASK] Look into parameter transforms: 0->1 at inlet
- [TASK] Sometimes simulations fail for no reason. Check out timeouts in CADET-Match
- [TASK] Run plots in subprocess, look at how to create multiple plots safely 
- [TASK] Implement match_solution_times config setting
- [TASK] Implement gradient search after GA
- [TASK] look at pareto front
- [TASK] CMAES optimizer: single objective
- [TASK] Use geometric mean for combining multiple objectives in to single objective
- [TASK] Implement checkpointing: pickle data
- [TASK] Adjust Verbose Display according to algorithm used
- [TASK] Random seeds
- [TASK] Implement better scores: Check out CADET-Match
- [TASK] Make sure tests delete temp files
- [TASK] Write unit tests for all classes
- [TASK] Look at save_history = True
- [CRIT] For the split-chromatogram problem, we know that the axial dispersion in once radial shell won't affect the chromatogram in another, so it does have a constraint. Is there a way to constrain the parameters that way? Or does it just mean we solve the system serially? 
- [TASK] Unified interface/method for deep getting and setting from/to a Dict or dict
