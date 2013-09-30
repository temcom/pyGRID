import unittest
import xml.etree.ElementTree as ET
import mock
import re

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
            write_calls = handle.write.call_args_list
            assert len(write_calls) == 3
            
            bash_code = write_calls[0][0][0]
            assert error_handling_bash_code in bash_code
            assert '#!/usr/bin/env qsub' in bash_code
            assert '#$ -e $JOB_NAME.o$JOB_ID.$TASK_ID' in bash_code
            assert '#$ -m es' in bash_code
            assert '#$ -j y' in bash_code
            assert '#$ -M sabbatini@physics.uq.edu.au' in bash_code
            assert '#$ -o $JOB_NAME.$JOB_ID.$TASK_ID' in bash_code
            assert '#$ -N basicTest' in bash_code
            assert '#$ -S /bin/bash' in bash_code
            assert '#$ -cwd' in bash_code
            assert 'echo "Basic Test"' in bash_code
            
            bash_code = write_calls[2][0][0]
            assert error_handling_bash_code in bash_code
            assert '#!/usr/bin/env qsub' in bash_code
            assert '#$ -e $JOB_NAME.o$JOB_ID.$TASK_ID' not in bash_code
            assert '#$ -m es' in bash_code
            assert '#$ -j y' in bash_code
            assert '#$ -M sabbatini@physics.uq.edu.au' in bash_code
            assert '#$ -o $JOB_NAME.$JOB_ID.$TASK_ID' not in bash_code
            assert '#$ -N basicTest' in bash_code
            assert '#$ -S /bin/bash' in bash_code
            assert '#$ -cwd' in bash_code
            assert 'echo "Basic Test"' in bash_code
            
            aux_code = write_calls[1][0][0]
            assert '<?xml version="1.0" ?>' in aux_code
            assert '<jobs>' in aux_code
            assert '</jobs>' in aux_code
            # make sure the job element appears only once in the right form
            job_list = re.finditer('<job JOB_ID="4" JOB_NAME="basicTest"/>', aux_code)
            assert sum(1 for s in job_list) == 1
    
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
            
            handle = fake_file()
            write_calls = handle.write.call_args_list
            assert len(write_calls) == 3
            bash_code = write_calls[0][0][0]
            assert '#$ -N inheritanceTest' in bash_code
                                    
            aux_code = write_calls[1][0][0]
            assert 'JOB_NAME="inheritanceTest"' in aux_code
            assert 'array="1-10"' in aux_code
    
    @mock.patch('subprocess.Popen')
    def test_parSpace_submission(self,fake_popen):
        fake_popen().stdout.read.return_value = '4'
        sim_element = find_sim_element(self.root,'parSpaceTest')
        gridJob = pyGRID(sim_element, self.parent_map)
        with mock.patch('__builtin__.open', mock.mock_open(), create=True) as fake_file:
            gridJob.submit()
            popen_calls = fake_popen.call_args_list
            # we have 2 parameters of 3 values each so there are 9 combinations to be run
            # there is also an empty popen call to initialise the thing
            assert len(popen_calls) == 10
            
            # let's extract the strings of the qsub calls and for file write calls
            qsub_calls = [popen_calls[i][0][0] for i in range(1,len(popen_calls))]
            handle = fake_file()
            bash_code = [handle.write.call_args_list[i][0][0] for i in range(0,len(handle.write.call_args_list))]
            aux_code = bash_code.pop(9)
            
            par_names = ('Amp','omega')
            par_values = [(2.0,1.0), (2.0,5.5), (2.0,10.0), (5.0,1.0), (5.0,5.5), 
                          (5.0,10.0), (6.0,1.0), (6.0,5.5), (6.0,10.0)]
            # check that qsub get's called for every combination of the parameters with
            # the right environment switch
            for c in par_values:
                current_comb = zip(par_names, c)
                var_strings = []
                for pair in current_comb:
                    var_strings.append('='.join(str(x) for x in pair))
                var_string = '-v ' + ','.join(var_strings)
                assert any(var_string in s for s in qsub_calls)
                output_string = '$JOB_NAME.$JOB_ID.$PAR_omega.$PAR_Amp'
                output_string = output_string.replace('$PAR_Amp',str(c[0]))
                output_string = output_string.replace('$PAR_omega',str(c[1]))
                output_string = '#$ -o ' + output_string
                assert any(output_string in s for s in bash_code)
            assert all('echo "Parameter space test"' in s for s in bash_code)
            assert all('echo $omega' in s for s in bash_code)
            assert all('echo $Amp' in s for s in bash_code)
            
            # check that we have recorded 9 submitted jobs
            job_list = re.finditer('JOB_NAME="parSpaceTest" array="1-10"', aux_code)
            assert sum(1 for s in job_list) == 9
            
            # check that each parameter value has been called exactly three times
            # this is because we have 3 values of each parameters hence the 3x3 calls
            assert sum(1 for s in re.finditer('Amp="2.0"', aux_code)) == 3
            assert sum(1 for s in re.finditer('Amp="5.0"', aux_code)) == 3
            assert sum(1 for s in re.finditer('Amp="6.0"', aux_code)) == 3
            assert sum(1 for s in re.finditer('omega="1.0"', aux_code)) == 3
            assert sum(1 for s in re.finditer('omega="5.5"', aux_code)) == 3
            assert sum(1 for s in re.finditer('omega="10.0"', aux_code)) == 3

if __name__ == '__main__':
    unittest.main()