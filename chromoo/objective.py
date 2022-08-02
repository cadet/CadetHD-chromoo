from dataclasses import dataclass, field
from chromoo.utils import readArray, readChromatogram

from typing import Optional
import numpy as np

@dataclass(init=True, order=True, repr=True, frozen=True)
class Objective: 
    """
    A class to store the objective paths and reference values, and evaluate a simulation's score.
    """
    name: str
    path: str
    filename: str
    shape: tuple = field(default_factory=tuple)
    times: str = ''
    combine_scores_axis: Optional[int] = None
    score: str = 'sse'
    x0: np.ndarray = np.array([])
    y0: np.ndarray = np.array([])

    def __post_init__(self): 
        """ 
        Read reference data if timestep data is separate or provided with the curves.
        Time data could be separated when dealing with, for instance, bulk output data, 
        which has a shape of (nts, ncol, nrad, ncomp). In that case, reshape
        the array to the given shape.
        """
        if self.times: 
            x0 = readArray(self.times)
            y0 = readArray(self.filename)

            if x0.shape == y0.shape: 
                object.__setattr__(self, 'shape', x0.shape)
            else: 
                y0 = y0.reshape((self.shape))

            object.__setattr__(self, 'x0', x0) 
            object.__setattr__(self, 'y0', y0)
        else: 
            x0, y0 = readChromatogram(self.filename)
            object.__setattr__(self, 'x0', x0)
            object.__setattr__(self, 'y0', y0)

    def evaluate(self, sim): 
        y = sim.get(self.path)
        y0 = self.y0
        sses = np.sum((y0 - y)**2)
        if self.combine_scores_axis is not None: 
            sses = np.average(sses, axis=self.combine_scores_axis)
        return sses.flatten()

    def split(self, sim):
        y = sim.get(self.path)

        # Move time axis to the end, and reshape array
        return np.moveaxis(y, 0, -1).reshape(-1,y.shape[0]).squeeze()
