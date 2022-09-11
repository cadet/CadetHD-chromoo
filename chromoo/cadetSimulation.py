from addict import Dict
from cadet import Cadet
from chromoo.utils import deep_get, keystring_todict, readChromatogram, readArray
from pathlib import Path
from ruamel.yaml import YAML
from typing import Any
from typing import TypeVar, Callable, Any, Optional

from chromoo.scores import scores_dict

import re
import os
import random
import string
import numpy as np
import subprocess

T = TypeVar("T")

cadetpath = subprocess.run(['which', 'cadet-cli'], capture_output=True, text=True ).stdout.strip()
Cadet.cadet_path = cadetpath

class CadetSimulation(Cadet): 
    def get(self, path:str, vartype:Callable[[Any],T]=Any, default=None, choices=[]) -> T: 
        """ Returns the value of a dot-separated path in the simulation data """
        return deep_get(self.root, path, vartype=vartype, default=default, choices=choices)

    def set(self, path:str, value:Any):
        """ Set a value in the simulation data at a given dot-separated path """
        dic = self.root

        for key in path.split('.'):
            dic = dic[key]

        dic = value

    def take(self, path:str, indices, axis:int): 
        """ Take data at indices on axis of an n-dimensional array """
        array = self.get(path, vartype=np.array)
        return np.take(array, indices=indices, axis=axis)

    def take_average(self, path:str, take_indices, take_axis:int, avg_axis:int, avg_x:list):
        """ Take data slice, then average it along another axis """
        array = self.get(path, vartype=np.array)
        taken = np.take(array, indices=take_indices, axis=take_axis)
        return np.trapz(taken, x=avg_x, axis=avg_axis) / (max(avg_x) - min(avg_x)) 

    def get_shape_pre(self, path:str): 
        """ A hack to pre-emptively know what the cadet output path shape is """
        unit = re.findall(r'unit_\d+', path)[0]
        output_type = path.split('.')[-1].split('_')[1]
        nts = len(self.root.input.solver.user_solution_times)

        ncol = self.root.input.model[unit].discretization.ncol
        nrad = self.root.input.model[unit].discretization.nrad
        ncomp = self.root.input.model[unit].ncomp
        npar = self.root.input.model[unit].npar

        ## WARNING: Haven't doublechecked this
        if output_type == 'outlet': 
            return (nts,)
        elif output_type == 'bulk': 
            return tuple(filter(None, (nts, ncol, nrad, ncomp)))
        elif output_type == 'particle': 
            return tuple(filter(None, (nts, ncol, nrad, npar)))
        elif output_type == 'solid': 
            return tuple(filter(None, (nts, ncol, nrad, npar)))
        else: 
            raise NotImplementedError


    def load_file(self, fname: str) -> None: 
        """ Load a simulation from either h5 or yaml file """
        ext = Path(fname).suffix

        if ext == ".h5":
            self.load_h5(fname)
        elif ext == ".yaml" or ext == ".yml" :
            self.load_yaml(fname)
        else:
            raise(RuntimeError('Invalid simulation file!'))

    def load_h5(self, filename: str):
        """ Load a cadet simulation file """
        self.filename = filename
        self.load()

    def load_yaml(self, filename:str):
        """ Load a YAML config for CADET """
        yaml=YAML(typ='safe')
        yaml.default_flow_style=False
        ext = Path(filename).suffix

        self.filename = filename.replace(ext, '.h5')
        self.root = Dict(yaml.load(Path(filename)))

    def update_parameters(self, x, parameters): 
        """
        Update parameters with values in x.
        """
        prev_len = 0
        for p in parameters:
            cur_len = p.length

            if p.type == 'element' :
                arr = self.root
                for key in p.path.split('.'):
                    arr = arr[key]
                value = x[prev_len : prev_len + cur_len]
                for idx_len,idx_arr in zip(range(cur_len), p.index):
                    arr[idx_arr] = value[idx_len]
                cur_dict = keystring_todict(p.path, arr)

                ## NOTE: Hack to copy flowrate values within the connections matrix
                if p.copy_to_path: 
                    arr2 = self.root
                    for key in p.copy_to_path.split('.'):
                        arr2 = arr2[key]
                    for idx_len,idx_copy_list in zip(range(cur_len), p.copy_to_index):
                        for idx_copy in idx_copy_list: 
                            arr2[idx_copy] = value[idx_len]
                    cur_dict.update(keystring_todict(p.copy_to_path, arr2))

            else:
                cur_dict = keystring_todict(p.path, x[prev_len : prev_len + cur_len])

                ## NOTE: Don't need this, so commented for safety, but written for generality
                # if p.copy_to_path: 
                #     cur_dict.update(keystring_todict(p.copy_to_path, x[prev_len : prev_len + cur_len]))

            self.root.update(cur_dict)
            prev_len += p.length


    def run_with_parameters(self, x, parameters, name:Optional[str]=None, tempdir:Path=Path('temp'), store:bool=False): 
        """ 
        Run the simulation with a given set of parameters. 
            -> x: parameter values
            -> parameter: dict with the following keys
                  - name: str
                  - type: scalar | vector | element
                  - length: <int>
                  - index: <int>
                  - path: str # input.model.unit_002.col_dispersion
                  - min_value: float 
                  - max_value: float
        """

        if name:
            self.filename = name
        else:
            self.filename = tempdir.joinpath('temp' + ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=6)) + '.h5')

        self.update_parameters(x, parameters)

        self.save()

        try:
            self.run(check=True)
        except subprocess.CalledProcessError as error:
            print(f"{self.filename} failed: {error.stderr.decode('utf-8').strip()}")
            print(f"Parameters: {x}\n")
            raise(RuntimeError("Simulation Failure"))

        self.load()

        if not store:
            os.remove(self.filename)

    def combine_port_breakthroughs(self, unit:int, comp:int=0, switch:int=0): 

        solution_unit = self.root.output.solution[f'unit_{unit:03d}']

        keys = [ key 
                for key in solution_unit.keys()
                if f'comp_{comp:03d}' in key if 'outlet' in key]

        nrad = self.root.input.model[f'unit_{unit:03d}'].discretization.nrad

        solutions = np.stack([ solution_unit[key] for key in keys ])

        assert(len(keys) == nrad)

        connections = self.root.input.model.connections[f'switch_{switch:03d}'].connections
        assert self.root.input.model.connections.connections_include_ports == 1
        connections = np.reshape(connections, (-1,7))
        my_unit_filter = np.asarray([unit])

        # Input flowrates into this unit
        filtered_connections = connections[np.in1d(connections[:,1], my_unit_filter)]

        # Sort by current unit's ports
        filtered_connections = filtered_connections[filtered_connections[:,3].argsort()]
        # Find indices where ports change
        d = np.diff(filtered_connections[:,3])
        e = np.where(d)[0]
        indices = np.r_[0,e+1]
        # Reduce (add) at/upto the given indices
        # Essentially adds all incoming flowrates, since we only extract flowrates
        flowrates = np.add.reduceat(filtered_connections, indices, axis=0)[:,6]

        assert(len(flowrates) == nrad)

        return np.sum(solutions.T * flowrates, axis=1) / sum(flowrates)


def new_run_and_eval(x, sim, parameters, objectives, name:Optional[str]=None, tempdir:Path=Path('temp'), store:bool=False): 
    simulation = CadetSimulation(sim.root)
    simulation.run_with_parameters(x, parameters, name, tempdir, store)

    results = np.hstack(list(map(lambda obj: obj.evaluate(simulation), objectives)))

    return results
