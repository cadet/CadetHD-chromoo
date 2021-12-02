"""
ChroMOO
========

    PyMOO for chromatography
"""

name = 'chromoo'

# __version__ = pkg_resources.get_distribution("chromoo").version
__version__ = '0.1'
__author__ = 'Jayghosh Rao'
__credits__ = 'FZJ/IBG-1/ModSim'

# Imports
from .configHandler import ConfigHandler
from .chromooProblem import ChromooProblem
from .algorithmFactory import AlgorithmFactory
from .cache import Cache

from . import plotter
from . import utils
from . import log
