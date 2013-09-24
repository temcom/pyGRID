import unittest
import xml.etree.ElementTree as ET
import mock

from pyGRID import *

auxilliary_strings = dict(basicTest = '<?xml version="1.0" ?>\n'\
                                      '<jobs>\n'\
                                      '\t<job JOB_ID="4" JOB_NAME="basicTest"/>\n'\
                                      '</jobs>\n',
                          inheritanceTest = '<?xml version="1.0" ?>\n'\
                                            '<jobs>\n'\
                                            '\t<job JOB_ID="4" JOB_NAME="inheritanceTest" array="1-10"/>\n'\
                                            '</jobs>\n')
                                      
bash_strings = dict(basicTest_1 = '#!/usr/bin/env qsub\n'\
                                  '# Written using pyGRID module\n'\
                                  '#$ -e $JOB_NAME.o$JOB_ID.$TASK_ID\n'\
                                  '#$ -m es\n'\
                                  '#$ -j y\n'\
                                  '#$ -M sabbatini@physics.uq.edu.au\n'\
                                  '#$ -o $JOB_NAME.$JOB_ID.$TASK_ID\n'\
                                  '#$ -N basicTest\n'\
                                  '#$ -S /bin/bash\n'\
                                  '#$ -cwd \n'\
                                  ' \n'\
                                  '# Code inserted by pyGRID\n'\
                                  '\n'\
                                  'function error_trap_handler()\n'\
                                  '{\n'\
                                  '        MYSELF="$0"              # equals to my script name\n'\
                                  '        LASTLINE="$1"            # argument 1: last line of error occurence\n'\
                                  '        LASTERR="$2"             # argument 2: error code of last command\n'\
                                  '        echo "pyGRID ERROR!"\n'\
                                  '        echo "${MYSELF}: line ${LASTLINE}: exit status of last command: ${LASTERR}"\n'\
                                  '}\n'\
                                  '\n'\
                                  'trap \'error_trap_handler ${LINENO} $?\' ERR\n'\
                                  '\n'\
                                  '\n'\
                                  'echo "Basic Test"\n'\
                                  ' \n'\
                                  'echo',
                    basicTest_2 = '#!/usr/bin/env qsub\n'\
                                  '# Written using pyGRID module\n'\
                                  '#$ -m es\n'\
                                  '#$ -j y\n'\
                                  '#$ -M sabbatini@physics.uq.edu.au\n'\
                                  '#$ -N basicTest\n'\
                                  '#$ -S /bin/bash\n'\
                                  '#$ -cwd \n \n'\
                                  '# Code inserted by pyGRID\n'\
                                  '\n'\
                                  'function error_trap_handler()\n'\
                                  '{\n'\
                                  '        MYSELF="$0"              # equals to my script name\n'\
                                  '        LASTLINE="$1"            # argument 1: last line of error occurence\n'\
                                  '        LASTERR="$2"             # argument 2: error code of last command\n'\
                                  '        echo "pyGRID ERROR!"\n'\
                                  '        echo "${MYSELF}: line ${LASTLINE}: exit status of last command: ${LASTERR}"\n'\
                                  '}\n'\
                                  '\n'\
                                  'trap \'error_trap_handler ${LINENO} $?\' ERR\n'\
                                  '\n'\
                                  '\n'\
                                  'echo "Basic Test"\n'\
                                  ' \n'\
                                  'echo')

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
    
    @mock.patch('subprocess.Popen')
    def test_basic_submission(self,fake_popen):
        fake_popen().stdout.read.return_value = '4'
        sim_element = find_sim_element(self.root,'basicTest')
        gridJob = pyGRID(sim_element, self.parent_map)
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as fake_file:
            gridJob.submit()
            assert fake_popen.called
            assert fake_popen.call_args[0][0] == 'qsub -terse basicTest.sh'
            assert fake_popen.call_args[1]['shell'] == True
            assert fake_popen.call_args[1]['stdout'] == subprocess.PIPE
            assert fake_popen.call_args[1]['stderr'] == subprocess.STDOUT
            
            fake_file.assert_any_call('basicTest.sh', 'w')
            fake_file.assert_any_call('basicTest.grid', 'w')
            handle = fake_file()
            handle.write.assert_any_call(auxilliary_strings['basicTest'])
            handle.write.assert_any_call(bash_strings['basicTest_1']) 
            handle.write.assert_any_call(bash_strings['basicTest_2'])
    
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
        
    @mock.patch('subprocess.Popen')
    def test_inheritance_submission(self,fake_popen):
        fake_popen().stdout.read.return_value = '4'
        sim_element = find_sim_element(self.root,'inheritanceTest')
        gridJob = pyGRID(sim_element, self.parent_map)
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as fake_file:
            gridJob.submit()
            assert fake_popen.called
            assert fake_popen.call_args[0][0] == 'qsub -terse -t 1-10 inheritanceTest.sh'
            assert fake_popen.call_args[1]['shell'] == True
            assert fake_popen.call_args[1]['stdout'] == subprocess.PIPE
            assert fake_popen.call_args[1]['stderr'] == subprocess.STDOUT
            
            fake_file.assert_any_call('inheritanceTest.sh', 'w')
            fake_file.assert_any_call('inheritanceTest.grid', 'w')
            handle = fake_file()
            handle.write.assert_any_call(auxilliary_strings['inheritanceTest'])

if __name__ == '__main__':
    unittest.main()