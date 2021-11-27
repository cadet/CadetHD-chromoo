# ChroMOO

Chromatography with PyMOO.

```{.mermaid format=pdf}
classDiagram
    class AlgorithmFactory{
    }
    class Problem{
        +Problem(sim, parameters[], reference)
        +Parameters[]
    }
    class Parameter{
        +name
        +path
        +length
        +min_value
        +max_value
        +todict(values:list)
    }
    class CadetSimulation{
        +sim
        +evaluate
        +evaluate_multi
        +create_template
    }
    class Plotter{
        +plot()
    }
```

# Classes

[DONE] ConfigHandler: Handle yaml and commandline args
AlgorithmFactory: Create algorithms: NSGA-III etc
Problem: 
    +Parameters[]
    +Problem(parameters[])
    +_evaluate()
    +update()
    +score()
    -nvar = sum of all param lengths
    -nobj = 1
    -nconstr = 0
    -xl = concat from param
    -xu = concat from param
Parameter: 
    +name
    +h5path
    +length
    +min_value
    +max_value
Score: depends on sse1 or sse2
    +

# UI
chromoo <h5> -r <csv/bin> -a <algo>

yaml config with specifics

# Dummy yaml config
simulation: hdf5
objectives: 
    csv: path_to_csv.csv
    score: sse
    path: /path/to/solution/arrays
    match_solution_times: true
parameters:
    - name: par1
      path: dispersion_path
      length: n
      min_value
      max_value
    - name: par2
      path: radial_dispersion_path
      length: n
      min_value
      max_value
algorithm: 
    name: nsga3
    populationSize: int

# Tests

ConfigHandler
    - Parse YAML correctly 
    - Parse commandline correctly 

ProblemFactory:
    - Do I need a factory?
    - Inputs: 
        - list of paths
        - list of values
        - list of lengths?: scalar, vector[length]
        - HANDLE scalars and vectors properly
        - OR just pass dicts with paths: values already
