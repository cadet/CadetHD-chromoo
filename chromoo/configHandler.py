"""

ConfigHandler class.

contract:
    - must read and store values from yaml config
    - must provide easy access to deep/nested values (deep_get -> get)

"""

from ruamel.yaml import YAML
from functools import reduce

from pathlib import Path

from chromoo.utils import loadh5

class ConfigHandler:

    def __init__(self):
        self.config = {}
        self.yaml=YAML(typ='safe')

    def read(self, fname):
        self.config = self.yaml.load(Path(fname))
        self.load()

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
        self.simulation =  loadh5(self.get('simulation', vartype=str()))

        self.objectives = self.get('objectives', None, list())
        self.parameters = self.get('parameters', None, list())
        self.algorithm = self.get('algorithm', None, dict())

