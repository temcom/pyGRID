import unittest
import xml.etree.ElementTree as ET

from pyGRID import *

class TestPyGRID(unittest.TestCase):

    def setUp(self):
        self.tree = ET.parse('tests/tests.xml')
        self.root = self.tree.getroot()
        self.parent_map = dict((c, p) for p in self.root.getiterator() for c in p)

    def test_find_sim_element(self):
        sim_element = find_sim_element(self.root,'basicTest')
        sim_name = sim_element.get(grid_file_kw['sim_name'])
        self.assertEqual( sim_name, 'basicTest' )
        self.assertEqual( len(list(sim_element)), 7)
        
    def test_basic_init(self):
        sim_element = find_sim_element(self.root,'basicTest')
        gridJob = pyGRID(sim_element, self.parent_map)
        self.assertEqual(gridJob.sim.args.N, 'basicTest')
        self.assertEqual(gridJob.sim.args.S, '/bin/bash')
        self.assertEqual(gridJob.sim.args.command, 'echo')
        self.assertTrue(gridJob.sim.args.cwd)
        self.assertEqual(gridJob.sim.args.j, 'y')
        
    def test_code_option(self):
        sim_element = find_sim_element(self.root,'basicTest')
        gridJob = pyGRID(sim_element, self.parent_map)
        self.assertTrue(error_handling_bash_code in gridJob.sim.args.code)
    
    def test_inheritance(self):
        sim_element = find_sim_element(self.root,'inheritanceTest')
        gridJob = pyGRID(sim_element, self.parent_map)
        # test that we inherited correctly the property of the parent job
        self.assertEqual(gridJob.sim.args.S, '/bin/bash')
        self.assertEqual(gridJob.sim.args.command, 'echo')
        self.assertTrue(gridJob.sim.args.cwd)
        self.assertEqual(gridJob.sim.args.j, 'y')
        
        # the array and the name are the only properties we changed in the child job
        self.assertEqual(gridJob.sim.args.N, 'inheritanceTest')
    
    def test_parse_array_notation(self):
        self.assertEqual(parse_array_notation('5'), 5)
        self.assertEqual(parse_array_notation('5-7'), [5, 6, 7])
        self.assertEqual(parse_array_notation('5-9:2'), [5, 7, 9])

    def test_parameters(self):
        sim_element = find_sim_element(self.root,'parSpaceTest')
        gridJob = pyGRID(sim_element, self.parent_map)
        self.assertTrue('Amp' in gridJob.parameters.keys())
        self.assertTrue('omega' in gridJob.parameters.keys())
        amp_values = gridJob.parameters['Amp']
        self.assertEqual(amp_values, [2.0, 5.0, 6.0])
        omega_values = gridJob.parameters['omega']
        self.assertEqual(omega_values, [1.0, 5.5, 10.0])
        params, combinations = gridJob._generate_param_space()
        self.assertEqual(params, ['Amp', 'omega'])
        self.assertEqual(combinations, [(2.0, 1.0), (2.0, 5.5), (2.0, 10.0), (5.0, 1.0), 
                                        (5.0, 5.5), (5.0, 10.0), (6.0, 1.0), (6.0, 5.5), 
                                        (6.0, 10.0)])

if __name__ == '__main__':
    unittest.main()