#!/usr/bin/env python3

""" General postprocesssing script. 
Dumps images into <postdir>.
"""

import  chromoo.post as post
from chromoo import ConfigHandler
from pathlib import Path
import os

config = ConfigHandler()
config.read('./chromoo.yaml')
config.load()
config.construct_simulation()

postdir = Path('post') 
postdir.mkdir(exist_ok=True)

# nproc = min(args.nproc or config.nproc, os.cpu_count())
nproc = 4
nsims = 1
mean='geometric'

opts = post.load_dataframe_sort('opts.csv', config.objective_names, sort_by=mean)
pops = post.load_dataframe_sort('populations', config.objective_names)

post.convergence(pops, mean, postdir)
for par in config.parameter_names:
    post.convergence(pops, par, postdir=postdir, name=f"convergence_{par}")

post.violin(opts[opts.columns[0:config.n_par]], postdir=postdir, percentile=100)
post.violin(opts[[mean]], postdir=postdir, name=f'violin_{mean}')

sims_opts = post.run_sims_parallel(opts.iloc[0:nsims], config, nproc, postdir=postdir, suffix='opts')
post.performance_range(sims_opts, config, postdir=postdir)
post.performance_combined(sims_opts, config, postdir=postdir, suffix=None)
post.write_objectives(sims_opts, config, postdir=postdir)

post.response_surface(pops, config.objective_names, config.parameter_names, postdir=postdir)

# post.performance_split(sims_opts[0], config, postdir=postdir)
# post.response_surface_split(pops, config, postdir=postdir)
