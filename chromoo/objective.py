from dataclasses import dataclass
from chromoo.utils import readArray, readChromatogram

@dataclass(init=True, order=True, repr=True, frozen=True)
class Objective:
    name: str
    path: str
    filename: str
    times: str = ''
    score: str = 'sse'
    
    def __post_init__(self): 
        if self.times: 
            object.__setattr__(self, 'x0', readArray(self.times)) 
            object.__setattr__(self, 'y0', readArray(self.filename)) 
        else: 
            x0, y0 = readChromatogram(self.filename)
            object.__setattr__(self, 'x0', x0)
            object.__setattr__(self, 'y0', y0)
