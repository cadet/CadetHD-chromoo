"""
    AlgorithmFactory

"""
class AlgorithmFactory:

    def __init__(self, algorithm_config: dict):
        if algorithm_config.get('name') == 'nsga3':
            from pymoo.algorithms.moo.nsga3 import NSGA3
            from pymoo.factory import get_reference_directions

            pop_size = algorithm_config.get('pop_size', 100)
            numRefDirs = pop_size
            ref_dirs = get_reference_directions("energy", 1, numRefDirs, seed=1)

            return NSGA3(pop_size=pop_size, ref_dirs=ref_dirs)
            
