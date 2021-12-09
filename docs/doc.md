---
geometry:
    - top=5mm
    - bottom=5mm
    - left=5mm
    - right=5mm
pagestyle: empty
---

# ChroMOO

Chromatography with PyMOO.

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
    AlgorithmFactory --> UNSGA3 : returns
    AlgorithmFactory --> NSGA3 : returns
```
