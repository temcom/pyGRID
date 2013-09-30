#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:45:20 2013

@author: Jacopo Sabbatini
"""

import argparse
import itertools
import subprocess
import re
import xml.etree.ElementTree as ET
from numpy import linspace
from xml.dom import minidom
from pyqsub import qsubOptions

# global dictionary to map the syntax of the xml to the internal representation
# This is useful in the case we want to change the syntax since we only need to change
# the corresponding mapping string here and not in the rest of the code
grid_file_kw = dict(parameter = 'parameter',
                parameters = 'parameters',
                par_name = 'name',
                par_inherit = 'inherit',
                code = 'code',
                root_element = 'simulations',
                sim_element = 'sim_element',
                sim_name = 'N')

aux_file_kw = dict(root = 'jobs',
                    job = 'job',
                    name = 'JOB_NAME',
                    id = 'JOB_ID',
                    array = 'array',
                    chrashes = 'crashes')

filename_prefixes = dict(parameters = 'PAR')

bash_file_extension = 'sh'                 
auxilliary_file_extension = 'grid'

pyGRID_error_identifier = "pyGRID ERROR!"
error_handling_bash_code = '\n'\
'function error_trap_handler()\n' \
'{{\n' \
'        MYSELF="$0"              # equals to my script name\n' \
'        LASTLINE="$1"            # argument 1: last line of error occurence\n' \
'        LASTERR="$2"             # argument 2: error code of last command\n' \
'        echo "{0}"\n' \
'        echo "${{MYSELF}}: line ${{LASTLINE}}: exit status of last command: ${{LASTERR}}"\n' \
'}}\n' \
'\n' \
'trap \'error_trap_handler ${{LINENO}} $?\' ERR\n'.format(pyGRID_error_identifier)

def find_sim_element(root,sim_name):
    try:
        # searching elements in an xml tree by attributes is available only for
        # Python 2.7+
        return root.find("./"+ grid_file_kw['sim_element'] 
                    +"[@{0}='{1}']".format(grid_file_kw['sim_name'],sim_name))
    except SyntaxError:
        # If the previous line failed then we have to search for element by looping
        # over all the simulation elements
        sim_elements = root.findall("./"+ grid_file_kw['sim_element'])
        for sim_element in sim_elements:
            current_name = sim_element.get(grid_file_kw['sim_name'])
            if current_name == sim_name:
                return sim_element

def writeXMLFile(element,filename):
    """Utility method that takes an xml element and write it to a file with pretty
    printing.

    Keyword arguments:
    element -- An ElementTree.Element defining an xml tree.
    filename -- String representing the location and name of the file to write
    """
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    text_file = open(filename, "w")
    text_file.write(reparsed.toprettyxml())
    text_file.close()

def parse_array_notation(array_string):
    """Parse a string defining an array of jobs and return an array of integers
    containing the TASK_IDs of the jobs. For the notation of an array job see qsub 
    man page.

    Keyword arguments:
    array_string -- The string defining the array job
    """
    pieces = re.split("-|:",array_string)
    if len(pieces) == 1:
        return int(pieces[0])
    if len(pieces) == 2:
        return range(int(pieces[0]),int(pieces[1])+1)
    if len(pieces) == 3:
        return range(int(pieces[0]),int(pieces[1])+1,int(pieces[2]))
    return []

def _substitute_in_templates(filename_template,substitution_dict):
    """Create a real filename by substituting the arguments in a template filename

    Keyword arguments:
    filename_template -- The string template to generate the filename
    substitution_dict -- a dictionary containing the keywords to substitute as keys and
                         the values to substitute them with as values
    """
    for k,v in substitution_dict.iteritems(): 
        filename_template = filename_template.replace(k,v)
    return filename_template

def _parse_parameter_value(par_value):
    par_value = par_value.split(':')
    if len(par_value) > 1:
        # the parameter range was specified in the format start:stop or start:samples:stop
        startValue = float(par_value[0])
        stopValue = float(par_value[-1])
        samples = 10
        if len(par_value) == 3:
            samples = int(par_value[1])                
        par_value = linspace(startValue, stopValue, samples)
    else:
        # the parameter values was specified as a list of numbers
        par_value = par_value[0].split()
    return [float(x) for x in par_value]

def _parse_parameters(par_element = None):
    """Parse the children of the parameter element and return a dictionary with the
    parameter names as keys and list of parameter values as values

    Keyword arguments:
    par_element -- An ElementTree.Element defining the parameters for
                   the job (default None). If None is passed returns an 
                   empty dictionary
    """
    parameters = dict()
    
    if par_element is None:
        return parameters
        
    for parameter in par_element.findall(grid_file_kw['parameter']):
        par_name = parameter.get(grid_file_kw['par_name'])
        par_value = parameter.text.strip(' \n\t')
        parameters[par_name] = _parse_parameter_value(par_value)
    return parameters

class InvalidNameError(Exception):
    def __str__(self):
        return "The simulation element representing the job must have a name."
        
class InvalidSimulatioNameError(Exception):
    def __init__(self, sim_name):
        self.sim_name = sim_name
    def __str__(self):
        return "The file defines no job named {0}".format(self.sim_name)

class pyGRID:
    
    def __str__(self):
        return '{0}\nParameters: {1}'.format(str(self.sim.args), str(self.parameters))

    def _parse_element(self, sim_element=None, parent_map=None):
        """Parse the children of the simulation element and insert them as arguments
        of the cluster job.

        Keyword arguments:
        sim_element -- An ElementTree.Element defining the parameters for
                       the job (default None).
        """
        if sim_element is None:
            return
        
        # check if the simulation element inherits from another sim_element
        inherit_from = sim_element.get(grid_file_kw['par_inherit'])
        if inherit_from and parent_map:
            # parse the options from the parent element first
            
            # simulation elements are always the children of the root element so we can
            # use the parent map to retrieve the root
            root_element = parent_map[sim_element]
            parent_element = find_sim_element(root_element,inherit_from)
            self._parse_element(parent_element,parent_map)
        
        # the name of the job is expressed as an attribute of the xml element so we deal
        # with it differently 
        job_name = sim_element.get(grid_file_kw['sim_name'])
        if (job_name is None) or (len(job_name) == 0):
            raise InvalidNameError
        self.sim.parse_and_add('-N {0}'.format(job_name))
        
        self.bashFilename = self.sim.args.N + '.' + bash_file_extension
        self.auxilliaryFilename = self.sim.args.N + '.' + auxilliary_file_extension
        
        # parse the parameters to pass to the job
        par_element = sim_element.find(grid_file_kw['parameters'])
        if par_element is not None:
            self.parameters = _parse_parameters(par_element)
        
        # parse the remaining qsub options
        for child in sim_element:
        
            if child.tag == grid_file_kw['parameters']:
                continue
        
            argument_value = child.text
            if argument_value is not None:
                argument_value = argument_value.strip(' \n\t')
        
            if child.tag == grid_file_kw['code']:
                self.sim.args.code = error_handling_bash_code + '\n\n' + argument_value
            elif child.tag == 't':
                self.array = argument_value
            elif child.tag == 'o':
                setattr(self,'output_filename_template',argument_value)
            elif child.tag == 'e':
                setattr(self,'error_filename_template',argument_value)
            else:
                if argument_value is not None:
                    self.sim.parse_and_add('-{0} {1}'.format(child.tag, argument_value))
                else:
                    self.sim.parse_and_add('-{0}'.format(child.tag))
    
    def __init__(self, sim_element=None, parent_map=None):
        """Initialise a pyGRID object from a simulation element and a map 
        of parents for every node in the xml tree.

        Keyword arguments:
        sim_element -- An ElementTree.Element defining the parameters for
                       the job (default None). If None is passed the
                       object is initialised with an empty qsubOptions object and an
                       empty dictionary for the parameters list
        parent_map -- A dictionary containing a list of nodes as keys and their parents
                      as values (default None). If None is passed the inherit attribute
                      of the simulation element is ignored.
        """
        self.sim = qsubOptions()
        self.parameters = dict()
        self.output_filename_template = "$JOB_NAME.o$JOB_ID.$TASK_ID"
        self.error_filename_template = "$JOB_NAME.o$JOB_ID.$TASK_ID"
        
        if sim_element is None:
            return
        
        # parse the element
        self._parse_element(sim_element,parent_map)
            
    def _generate_param_space(self):
        """Generate all the possible combinations of the parameters for the job.
        Returns a list of parameters and list of all possible combinations of the
        parameters values. If the job has no parameters then returns None for both.
        """
        if len(self.parameters) == 0:
            return None,None
        else:
            return self.parameters.keys(), [x for x in apply(itertools.product, 
                                                          self.parameters.values())]
    
    def _submit_job(self,parameter_list = None, array_string = None):
        """Utility method to submit a job to qsub. Return an ElementTree.Element object
        describing the job just submitted.
        
        Keyword arguments:
        parameter_list -- a list of pairs defining the name of the parameter and its value
                          for the job
        array_string   -- a string for submitting an array job
        """
        job = ET.Element(aux_file_kw['job'])
        job.set(aux_file_kw['name'],self.sim.args.N)
        
        output_filename = self.output_filename_template
        error_filename = self.error_filename_template
        
        execstring = ['qsub', '-terse']
        if parameter_list:
            param_string = []
            substitution_dict = dict()
            for pair in parameter_list:
                param_string.append('='.join(str(x) for x in pair))
                job.set('PAR_'+str(pair[0]),str(pair[1]))
                substitution_dict['$'+filename_prefixes['parameters']+'_'+str(pair[0])] = str(pair[1])
            param_string = ','.join(param_string)
            execstring.extend(['-v',param_string])
            output_filename = _substitute_in_templates(output_filename,substitution_dict)
            error_filename = _substitute_in_templates(error_filename,substitution_dict)

        self.sim.args.o = output_filename
        self.sim.args.e = error_filename  
        self.sim.write_qsub_script(self.bashFilename)      
        
        if array_string:
            execstring.extend(['-t',array_string])
            job.set(aux_file_kw['array'],array_string)
        
        execstring.append(self.bashFilename)
        execstring = ' '.join(execstring)
        p = subprocess.Popen(execstring, stdout = subprocess.PIPE, 
                                                stderr = subprocess.STDOUT, shell = True)
                
        # retrieve the job_id and add it to the job xml element
        jobID = p.stdout.read().strip(' \n\t')
        job.set(aux_file_kw['id'], jobID.split('.')[0])
        return job
    
    def submit(self):
        """Submit a job to the queue manager for every possible combination of the
        parameters of the simulation. It also writes an xml file holding the job_id from
        the queue manager for every job submitted with the list of the parameters passed
        and the array information.
        """
        
        # Root element for the xml holding the information about job submission IDs
        jobs = ET.Element(aux_file_kw['root'])
        
        array_string = getattr(self,'array',None)
        
        params, combinations = self._generate_param_space()
        if combinations is None:
            job = self._submit_job(array_string = array_string)
            jobs.append(job)
        else:
            for c in combinations:
                job = self._submit_job(parameter_list = zip(params,c), 
                                                            array_string = array_string)
                jobs.append(job)
        # write the xml file with the job IDs
        writeXMLFile(jobs,self.auxilliaryFilename)
        
        # create the bash script without reference to the output/error filenames so that
        # the user can use it
        delattr(self.sim.args,'o')
        delattr(self.sim.args,'e')
        self.sim.write_qsub_script(self.bashFilename)
    
    def scan_crashed_jobs(self, filepath = None):
        """Loads the auxiliary file for this job, generate the filenames for the streams
        and check them for runtime errors.
        
        Keyword arguments:
        filepath -- the path of file from which to parse the list of jobs in case it has 
                    been renamed from pyGRID default. If None the pyGRID default is used
        """
        if filepath is None:
            filepath = self.auxilliaryFilename
        file_string = open(filepath,'r').read()
        root = ET.fromstring(file_string)
        for job_element in root.findall(aux_file_kw['job']):
            crashed, crash_indices = self.search_stream_for_error(job_element.attrib)
            if crashed:
                crashes_element = ET.Element(aux_file_kw['crashes'])
                if crash_indices is not None:
                    crashes_element.text = ' '.join(str(i) for i in crash_indices)
                job_element.append(crashes_element)
        writeXMLFile(root,self.auxilliaryFilename)
        
    def search_stream_for_error(self,job_attributes):
        """Search the stream files of job defined by the arguments for errors and return
        True if any is encountered

        Keyword arguments:
        job_attributes -- a dictionary of attributes defining the job
        """
        array_string = job_attributes.pop(aux_file_kw['array'],None)
        keywords = ['$'+str(x) for x in job_attributes.keys()]
        
        output = _substitute_in_templates(self.output_filename_template,
                                             dict(zip(keywords,job_attributes.values())))
        error = _substitute_in_templates(self.error_filename_template,
                                             dict(zip(keywords,job_attributes.values())))
        if array_string is not None:
            array_indices = parse_array_notation(array_string)
            crash_indices = []
            for index in array_indices:
                task_output = _substitute_in_templates(output,{'$TASK_ID':str(index)})
                task_error = _substitute_in_templates(error,{'$TASK_ID':str(index)})
                if (self._search_file_for_error(task_output) or self._search_file_for_error(task_error)):
                    crash_indices.append(index)
            if len(crash_indices):
                return True, crash_indices
        else:
            return (self._search_file_for_error(output) or 
                                                self._search_file_for_error(error)), None
        return False, None
    
    def _search_file_for_error(self, filename):
        try:
            with open(filename, "r") as output_file:
                output_string = output_file.read()
                if pyGRID_error_identifier in output_string:
                    return True
        except IOError:
            print "The stream file {0} for the job does not exists".format(filename)
        return False
    
    def resubmit_crashed(self):
        self.scan_crashed_jobs()
        
        self.sim.write_qsub_script(self.bashFilename)
        
        tree = ET.parse(self.auxilliaryFilename)
        root = tree.getroot()
        for job_element in root.findall(aux_file_kw['job']):
            crash_element = job_element.find(aux_file_kw['crashes'])
            if crash_element is None:
                continue
            crashed_indices = crash_element.text.split()
            
            parameters = job_element.attrib
            parameters.pop(aux_file_kw['name'],None)
            parameters.pop(aux_file_kw['id'],None)
            parameters.pop(aux_file_kw['array'],None)
            
            if len(crased_indices) == 0:
                # if there are no crashed indices it means the job wasn't an array job so
                # it's safe to just resubmit it
                new_job_element = self._submit_job(zip(parameters.keys(),
                                                                parameters.values()))
                # substitute the old job element with the new one
                root.remove(job_element)
                root.append(new_job_element)
            else:
                root.remove(job_element)
                for i in crash_indices:
                    new_job_element = self._submit_job(zip(parameters.keys(),
                                                                parameters.values()),i)
                    root.append(new_job_element) 
        

def main():
    # define the arguments for the python script
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",help="Specify which file pyGRID should use to load definitions of the simulations")
    
    simulation_group = parser.add_mutually_exclusive_group()
    simulation_group.add_argument("-s", "--simulation",help="The name of the simulation to use")
    simulation_group.add_argument("-a", "--all",action='store_true',help="pyGRID will apply the actions specified to every simulation defined in the xml file")
    
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument("-w","--write",action='store_true',help="If write is specified then pyGRID will create the bash script in the current directory")
    action_group.add_argument("-b","--submit",action='store_true',help="If submit is specified then pyGRID will submit the job otherwise it will simply create the bash script")
    action_group.add_argument("-c","--crashes",action='store_true',help="pyGRID will scan the stream files for a job and determine the ones that crashed")
    action_group.add_argument("-r","--resubmit",action='store_true',help="pyGRID will resubmit the crashed jobs parsed from stream files")

    # parse the arguments from the command line
    args = parser.parse_args()

    # read the xml file, parse it and create the parent map 
    tree = ET.parse(args.file)
    root = tree.getroot()
    parent_map = dict((c, p) for p in root.getiterator() for c in p)
    
    if args.simulation:
        # if the user requested a particular job we create it and submit it
        matching_sim_element = find_sim_element(root,args.simulation)
        if matching_sim_element is None:
            raise InvalidSimulatioNameError(args.simulation)
        gridJob = pyGRID(sim_element = matching_sim_element, parent_map = parent_map)
        if args.submit:
            gridJob.submit()
        if args.write:
            gridJob.sim.write_qsub_script(gridJob.bashFilename)
        if args.crashes:
            gridJob.scan_crashed_jobs()
        if args.resubmit:
            gridJob.resubmit_crashed()
    if args.all:
        # we create job objects for every simulation in the xml file
        for sim_element in root.findall(grid_file_kw['sim_element']):
            gridJob = pyGRID(sim_element = sim_element, parent_map = parent_map)
            if args.submit:
                gridJob.submit()
            if args.write:
                gridJob.sim.write_qsub_script(gridJob.bashFilename)
            if args.crashes:
                gridJob.scan_crashed_jobs()
            if args.resubmit:
                gridJob.resubmit_crashed()