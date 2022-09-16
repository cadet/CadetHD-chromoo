"""
ChroMOO
========

    PyMOO for chromatography
"""

import pkg_resources
import git

def git_version():
    """ Return version with local version identifier. """
    try: 
        repo = git.Repo('.', search_parent_directories=True)
        repo.git.status()
        sha = repo.head.commit.hexsha
        sha = repo.git.rev_parse(sha, short=6)
        if repo.is_dirty():
            return '{sha}.dirty'.format(sha=sha)
        else:
            return sha
    except git.InvalidGitRepositoryError: 
        return None

name = 'chromoo'
__version__ = '0.1'
# If run locally, return the actual git version, otherwise, return the version installed.
__git_version__ = git_version() or pkg_resources.get_distribution("chromoo").version
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
from . import transforms

from . import cadetSimulation
from . import scores
