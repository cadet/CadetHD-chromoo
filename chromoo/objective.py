from dataclasses import dataclass, field
from typing import List, Literal, Any

@dataclass(init=True, order=True, repr=True, frozen=True)
class Objective:
    name: str
    path: str
    filename: str
    times: str = ''
    score: str = 'sse'
    match_solution_times: bool = True
