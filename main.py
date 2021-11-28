from chromoo import ChromooProblem, AlgorithmFactory, ConfigHandler

from pymoo.optimize import minimize
import argparse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs=1, help="yaml config file")
    args = vars(ap.parse_args())

    config = ConfigHandler()
    config.read(args['file'][0])

    algo = AlgorithmFactory(config.algorithm).get_algorithm()
    prob = ChromooProblem(config.simulation, config.parameters, config.objectives)

    res = minimize(
            prob, 
            algo,
            seed=122,
            termination=('n_gen', 10), 
            verbose=True
    )

    print(f"Took {res.exec_time} seconds to terminate.")
    print(f"Fitted Dispersion: {res.X}")
    print(f"SSE: {res.F}")

    # return res.X

    ## TODO: Run final simulation with res.X 
    ## TODO: plots

if __name__ == "__main__":
    main()
