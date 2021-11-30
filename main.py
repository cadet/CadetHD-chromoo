from chromoo import __version__
from chromoo import ChromooProblem, AlgorithmFactory, ConfigHandler
from chromoo.utils import loadh5, plotter
from chromoo.log import Logger

from pymoo.optimize import minimize
from pymoo.util.termination.default import MultiObjectiveDefaultTermination

import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs=1, help="yaml config file")
    args = vars(ap.parse_args())

    logger = Logger()
    logger.info("Starting chromoo")
    logger.note('chromoo version', __version__)

    config = ConfigHandler()
    config.read(args['file'][0])
    config.load()
    config.construct_simulation()

    algo = AlgorithmFactory(config.algorithm).get_algorithm()
    prob = ChromooProblem(config.simulation, config.parameters, config.objectives, nproc=config.nproc)

    term = MultiObjectiveDefaultTermination(
        x_tol       = config.termination.x_tol,
        cv_tol      = config.termination.cv_tol,
        f_tol       = config.termination.f_tol,
        nth_gen     = config.termination.nth_gen,
        n_last      = config.termination.n_last,
        n_max_gen   = config.termination.n_max_gen,
        n_max_evals = config.termination.n_max_evals
    )

    res = minimize(
            prob, 
            algo,
            term,
            seed=122,
            verbose=True
    )

    logger.info(f"Took {res.exec_time:.2f} seconds to terminate.")
    logger.info(f"Fitted Parameters: {res.X}")
    logger.info(f"SSE: {res.F}")

    prob.evaluate_sim(res.X, name='final.h5')
    sim = loadh5('final.h5')
    plotter(sim, config.objectives) 

    if not config.store_temp:
        import shutil
        shutil.rmtree(prob.tempdir)

    logger.info("Done :)")

if __name__ == "__main__":
    main()
