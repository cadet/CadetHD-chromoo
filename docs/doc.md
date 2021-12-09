---
geometry:
    - top=5mm
    - bottom=5mm
    - left=5mm
    - right=5mm
pagestyle: empty
---

# ChroMOO

Chromatography with PyMOO. This document, like the code, is a work in progress.

```{.mermaid format=pdf}
classDiagram
    class AlgorithmFactory{
        +init(string)
        +get()
    }
    class Problem{
    }
    class ChromooProblem{
        +sim
        +parameters
        +objectives
        +nproc: int
        +init(sim, parameters, objectives, nproc)
        +_evaluate()
    }
    class Simulation{
        +run_sim()
        +evaluate_sim()
        +run_and_eval()
    }
    class Cache{
        +database[]
        +plot_stuff()
    }
    class Callback{
        +cache
        +update_cache()
        +save_last_best()
    }
    class UNSGA3{
    }
    class NSGA3{
    }
    class ConfigHandler{
        +config: dict
        +necessary_attribs 
        +get()
    }

    Problem <|-- ChromooProblem
    ChromooProblem --> Simulation : uses
    AlgorithmFactory --> UNSGA3 : returns
    AlgorithmFactory --> NSGA3 : returns
    Callback --> Cache : has
```
