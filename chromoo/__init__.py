"""
ChroMOO
========

    PyMOO for chromatography
"""

import pkg_resources

name = 'chromoo'

# __version__ = pkg_resources.get_distribution("chromoo").version
__author__ = 'Jayghosh Rao'
__credits__ = 'FZJ/IBG-1/ModSim'

# Imports
from .configHandler import ConfigHandler
from .chromooProblem import ChromooProblem
from .algorithmFactory import AlgorithmFactory

from . import utils
