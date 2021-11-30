# ChroMOO (or chromoo)

Chromatography optimization with cadet and pymoo. I built this because CADET-Match didn't offer optimization with certain parameters and objectives. For example, optimizing SOLUTION_BULK is not possible currently. Input of vector parameters is also currently not possible.

While I haven't yet fully looked through the source code of CADET-Match, I would like to take inspiration from it while building chromoo. Eventually, when I get a better understanding of pymoo, cadet-match and the problem, I believe it should be possible to merge the code into CADET-Match.

# Installation

```
pip install .
```

# Usage

Chromoo requires a YAML config file. I use ruamel.yaml, which allows using YAML v1.2, meaning comments are allowed, and exponential notation is better parsed.

A template of the config follows:

```
filename: 10k-mono.mono1d.h5
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

Some notes:
- It runs multiple cadet simulations from a pool size of `nproc` for every evaluation of a population.
- parameters and objectives are **lists**
- Objective targets can be provided as an (times,values) csv file in `objectives.filename` or with the times separately specified in `objectives.times`
    - chromatograms already contain times, so it's easier to just provide the filename
    - solution_bulk data obtained from 3D sims are multidimensional, and we would like to try fitting the whole thing as a flat vector first
- The `solution_times` section of the provided cadet simulation will be changed to match those of `objectives[0]` exactly.

# TODO
- [TASK] Write unit tests for all classes
- [TASK] Implement logging
- [TASK] Implement better scores
- [TASK] Implement match_solution_times config setting
