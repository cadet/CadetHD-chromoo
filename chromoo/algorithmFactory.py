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
            dimensions = algorithm_config.get('n_obj')
            ref_dirs = get_reference_directions("energy", dimensions, numRefDirs, seed=204)

            self.algo = NSGA3(pop_size=pop_size, ref_dirs=ref_dirs)
        else:
            raise(RuntimeError("Invalid algorithm!"))

    def get_algorithm(self):
        return self.algo
            
