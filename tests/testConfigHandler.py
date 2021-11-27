import unittest

from chromoo import ConfigHandler

import logging

class TestConfigHandler(unittest.TestCase):
    def __init__(self, methodName='runTest'):

        LOG_FORMAT = '%s(levelname): %(message)s'
        logging.basicConfig(filename = 'testConfigHandler.log', level=logging.DEBUG, format=LOG_FORMAT)
        self.logger = logging.getLogger()
        self.logger.info('Instantiating TestConfigHandler')

        super().__init__(methodName)

    def test_init(self):
        config = ConfigHandler()
        self.assertDictEqual(config.config, {})

    def test_read(self):
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

    # def test_load(self):
    #     config = ConfigHandler()
    #
    #     config.config = {
    #         'simulation': 'cadet.h5',
    #         'objectives': [
    #             {
    #                 'csv': 'chromatogram.csv',
    #                 'score': 'sse',
    #                 'path': 'output.solution.solution_unit_003_comp_000',
    #                 'match_solution_times': True
    #             }
    #         ],
    #         'parameters': [
    #             {
    #                 'name': 'axial',
    #                 'path': 'input.model.unit_002.col_dispersion',
    #                 'length': 1,
    #                 'min_value': 1.0e-9,
    #                 'max_value': 1.0e-4
    #             },
    #             {
    #                 'name': 'radial',
    #                 'path': 'input.model.unit_002.col_dispersion_radial',
    #                 'length': 1,
    #                 'min_value': 1.0e-9,
    #                 'max_value': 1.0e-4
    #             }
    #         ],
    #         'algorithm': {
    #             'name': 'nsga3',
    #             'pop_size': 100
    #         }
    #     }
    #
    #     config.load()
    #     self.assertEqual(
    #         {
    #             'name': 'nsga3',
    #             'pop_size': 100
    #         },
    #         config.algorithm
    #     )
            

if __name__ == '__main__':
    unittest.main()
