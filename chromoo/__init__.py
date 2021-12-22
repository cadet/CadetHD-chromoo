"""
ChroMOO
========

    PyMOO for chromatography
"""

import pkg_resources

name = 'chromoo'

# __version__ = pkg_resources.get_distribution("chromoo").version
__version__ = '0.1'
__git_version__ = pkg_resources.get_distribution("chromoo").version
__author__ = 'Jayghosh Rao'
__credits__ = 'FZJ/IBG-1/ModSim'

# Imports
from .configHandler import ConfigHandler
from .chromooProblem import ChromooProblem
from .callback import ChromooCallback
from .algorithmFactory import AlgorithmFactory
from .cache import Cache

from . import parameter
from . import objective

from . import simulation
from . import plotter
from . import utils
from . import log
