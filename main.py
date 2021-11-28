from chromoo import ChromooProblem, AlgorithmFactory, ConfigHandler

from pymoo.optimize import minimize
import argparse

from pymoo.util.termination.default import MultiObjectiveDefaultTermination

from chromoo.utils import keystring_todict, readChromatogram, deep_get
from matplotlib import pyplot as plt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs=1, help="yaml config file")
    args = vars(ap.parse_args())

    config = ConfigHandler()
    config.read(args['file'][0])

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

    print(f"Took {res.exec_time} seconds to terminate.")
    print(f"Fitted Dispersion: {res.X}")
    print(f"SSE: {res.F}")


    sim = config.simulation
    sim.filename = 'final.h5'

    # For every parameter, generate a dictionary based on the path, and
    # update the simulation in a nested way
    # TODO: Probably a neater way to do this
    # FIXME: This is copied from chromaproblem
    prev_len = 0
    for p in config.parameters:
        cur_len = p.length
        cur_dict = keystring_todict(p.get('path'), res.X[prev_len : prev_len + cur_len])
        sim.root.update(cur_dict)
        prev_len += p.length

    sim.save()

    runout = sim.run()
    if runout.returncode != 0:
        print(runout)
        raise RuntimeError
    sim.load()

    # with plt.style.context(['science']):
    for obj in config.objectives:
        fig, ax = plt.subplots()

        ## FIXME
        t0, c0 = readChromatogram("chromatogram-corrected.csv")

        t1 = sim.root.output.solution.solution_times
        c1 = deep_get(sim.root, obj.path)
        ax.plot(t0,c0, lw=1, ls='solid', label='reference')
        ax.plot(t1,c1, lw=1, ls='dashed', label='result')
        fig.savefig(f"chromoo_{obj.name}_result.pdf")

if __name__ == "__main__":
    main()
