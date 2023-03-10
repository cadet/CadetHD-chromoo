import unittest
from chromoo.cadetSimulation import CadetSimulation

class TestCadetSimulation(unittest.TestCase):

    def test_get_bulk_volume_1d(self): 
        sim = CadetSimulation()
        sim.load_file('tests/10k-mono.mono1d.yaml')
        sim.get_vol_array(2,'bulk')

    def test_get_bulk_volume_2d(self): 
        sim = CadetSimulation()
        sim.load_file('tests/10k-mono.mono2d.yaml')
        sim.get_vol_array(2, 'bulk')

    def test_get_internal_mass_1d(self): 
        sim = CadetSimulation()
        sim.load_file('tests/final_1d.h5')
        sim.post_internal_mass(2)

    def test_get_internal_mass_2d(self): 
        sim = CadetSimulation()
        sim.load_file('tests/final_2d.h5')
        sim.post_internal_mass(2)

    def test_postproc(self): 
        sim = CadetSimulation()
        sim.load_file('tests/final_2d.h5')
        # sim.root.output.solution.unit_002.solution_internal_mass =  sim.get_internal_mass(2)
        # print(list(sim.__class__.__dict__.keys()))
        CadetSimulation.__dict__['post_internal_mass'](sim, 2)

    def test_run_1d(self): 
        sim = CadetSimulation()
        sim.load_file('tests/10k-mono.mono1d.yaml')
        sim.save_run_load()
        data = sim.get('output.solution.unit_002.solution_bulk')
        sim.post_internal_mass(2)
        data = sim.get('output.post.unit_002.post_bulk_mass')
