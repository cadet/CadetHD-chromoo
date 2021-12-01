import unittest

from chromoo import ConfigHandler

import logging

class TestConfigHandler(unittest.TestCase):
    def __init__(self, methodName='runTest'):

        LOG_FORMAT = '[%(asctime)s] %(levelname)s: %(message)s'
        logging.basicConfig(
            filename = 'testConfigHandler.log', 
            level=logging.DEBUG, 
            format=LOG_FORMAT,
            filemode='w'
        )
        self.logger = logging.getLogger()
        self.logger.info('Instantiating TestConfigHandler')

        super().__init__(methodName)

    def test_init(self):
        """
            Test class initialization
        """
        self.logger.info("Running test_init()")
        config = ConfigHandler()
        self.assertDictEqual(config.config, {})

    # TODO: Run read tests for all vartypes
    def test_read(self):
        """
            Test the yaml reader of the config file
        """
        self.logger.info("Running test_read()")
        filename = 'test_config_file.yaml'
        with open(filename, 'w') as fp:
            fp.write('key: value')

        config = ConfigHandler()
        config.read(filename)
        self.assertDictEqual(config.config, {'key': 'value'})

    def test_get(self):
        config = ConfigHandler()

        config.config = {'key': 'value'}
        self.assertEqual( config.get('key'), 'value' )

        config.config = {'key1': { 'key2': 0.5 }}
        self.assertEqual( config.get('key1.key2'), 0.5 )

        config.config = {'key1': { 'key2': 0.5 }}
        self.assertEqual( config.get('key1.key2', vartype=float), 0.5 )

        config.config = {'key1': { 'key2': 0.5 }}
        with self.assertRaises(RuntimeError): config.get('key1.key2', vartype=int)

        config.config = {'key1': { 'key2': 'value' }}
        self.assertEqual('value', config.get('key1.key2', vartype=str()))

        config.config = {'key1': { 'key2': [ 'value1', 'value2'] }}
        self.assertEqual(['value1', 'value2'], config.get('key1.key2', vartype=list))

        config.config = {'key1': { 'key2': [ 'value1', 'value2'] }}
        self.assertEqual('value2', config.get('key1.key2', vartype=list)[1])

    def test_load(self):
        config = ConfigHandler()

        config.config = {
            'filename': 'cadet.h5',
            'objectives': [
                {
                    'name': 'outlet',
                    'filename': 'chromatogram.csv',
                    'score': 'sse',
                    'path': 'output.solution.solution_outlet_unit_003_comp_000',
                    'match_solution_times': True
                }
            ],
            'parameters': [
                {
                    'name': 'axial',
                    'path': 'input.model.unit_002.col_dispersion',
                    'length': 1,
                    'min_value': 1.0e-9,
                    'max_value': 1.0e-4
                },
                {
                    'name': 'radial',
                    'path': 'input.model.unit_002.col_dispersion_radial',
                    'length': 1,
                    'min_value': 1.0e-9,
                    'max_value': 1.0e-4
                }
            ],
            'algorithm': {
                'name': 'nsga3',
                'pop_size': 100
            }
        }

        config.load()
        self.assertEqual( 'cadet.h5', config.filename)
        self.assertEqual( 4, config.nproc)

        self.assertEqual( 'nsga3', config.algorithm.name)
        self.assertEqual( 100 , config.algorithm.pop_size)
        self.assertEqual( 100, config.algorithm.n_offsprings)

        self.assertEqual( 'axial', config.parameters[0].name)
        self.assertEqual( 'input.model.unit_002.col_dispersion', config.parameters[0].path)
        self.assertEqual( 1, config.parameters[0].length)
        self.assertEqual( 1.0e-9, config.parameters[0].min_value)
        self.assertEqual( 1.0e-4, config.parameters[0].max_value)

        self.assertEqual( 'outlet', config.objectives[0].name)
        self.assertEqual( 'output.solution.solution_outlet_unit_003_comp_000', config.objectives[0].path)
        self.assertEqual( 'sse', config.objectives[0].score)
        self.assertEqual( 'chromatogram.csv', config.objectives[0].filename)


if __name__ == '__main__':
    unittest.main()
