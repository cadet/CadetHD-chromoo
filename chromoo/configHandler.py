"""

ConfigHandler class.

contract:
    - must read and store values from yaml config
    - must provide easy access to deep/nested values (deep_get -> get)

"""

from ruamel.yaml import YAML
from functools import reduce

from pathlib import Path

from chromoo.utils import loadh5, readArray, readChromatogram

from addict import Dict

class ConfigHandler:

    def __init__(self):
        self.config = {}
        self.yaml=YAML(typ='safe')

    def read(self, fname):
        self.config = Dict(self.yaml.load(Path(fname)))
        self.load()
        self.construct_simulation()

    def get(self, keys, default=None, vartype=None, choices=[]):
        """
        Simpler syntax to get deep values from a dictionary
        > config.get('key1.key2.key3', defaultValue)

        - typechecking
        - value restriction
        """
        value = reduce(lambda d, key: d.get(key, None) if isinstance(d, dict) else None, keys.split("."), self.config)

        if value == None:
            if default != None:
                # self.logger.warn(keys, 'not specified! Defaulting to', str(default) or 'None (empty string)')
                print(keys, 'not specified! Defaulting to', str(default) or 'None (empty string)')
                value = default

        if vartype:
            if not isinstance(value, vartype):
                # self.logger.die(keys, 'has invalid type!', str(type(value)), 'instead of', str(vartype))
                print(keys, 'has invalid type!', str(type(value)), 'instead of', str(vartype))
                raise(RuntimeError('Invalid vartype'))

        if choices:
            if value not in choices:
                # self.logger.die(keys, 'has invalid value! Must be one of ', str(choices))
                print(keys, 'has invalid value! Must be one of ', str(choices))
                raise(RuntimeError('Invalid choice'))

        return value

    def load(self):
        """
        Assign values from the loaded dict to the object's attributes
        Centralizes the config value and type checking
        """
        self.filename=  self.get('filename', vartype=str())
        self.nproc=  self.get('nproc', vartype=int, default=4)

        # NOTE: Can be arbitrarily long
        # TODO: Find a way to check each objective/parameter for default keys and values
        self.objectives = [ Dict(x) for x in self.get('objectives', None, list()) ] 
        self.parameters = [ Dict(x) for x in self.get('parameters', None, list()) ]

        # If i'm passing a dict to a class, might be better to take the full dict, and then adjust the important subfields. Otherwise, I can just manually constrain the subfields for better sanity.
        # self.algorithm = Dict(self.get('algorithm', None, dict()))
        self.algorithm = Dict()

        self.algorithm.name = self.get('algorithm.name', 'nsga3', str(), ['nsga3'])
        self.algorithm.pop_size= self.get('algorithm.pop_size', 10, vartype=int)
        self.algorithm.n_offsprings = self.get('algorithm.n_offsprings', self.algorithm.pop_size, vartype=int)

        self.termination = Dict()
        self.termination.x_tol = self.get('termination.x_tol', 1e-12, float)
        self.termination.cv_tol = self.get('termination.cv_tol', 1e-6, float)
        self.termination.f_tol = self.get('termination.f_tol', 1e-10, float)
        self.termination.nth_gen = self.get('termination.nth_gen', 2, int)
        self.termination.n_last = self.get('termination.n_last', 5, int)
        self.termination.n_max_gen = self.get('termination.n_max_gen', 100, int)
        self.termination.n_max_evals = self.get('termination.n_max_evals', 1000, int)

    def construct_simulation(self):
        self.simulation =  loadh5(self.filename)

        # NOTE: Only the first objective is checked for timesteps
        if self.objectives[0].get('times'):
            t0 = readArray(self.objectives[0].times)
            self.objectives_contain_times = False
        else:
            t0,_ = readChromatogram(self.objectives[0].filename)
            self.objectives_contain_times = True

        self.simulation.root.input.solver.sections.section_times = [min(t0), max(t0)]
        self.simulation.root.input.solver.user_solution_times = t0
