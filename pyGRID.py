#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:45:20 2013

@author: Jacopo Sabbatini
"""

import argparse
import itertools
import subprocess
import xml.etree.ElementTree as ET
from numpy import linspace
from xml.dom import minidom
from pyqsub import qsubOptions

# global dictionary to map the syntax of the xml to the internal representation
# This is useful in the case we want to change the syntax since we only need to change
# the corresponding mapping string here and not in the rest of the code
_keywords = dict(parameter = 'parameter',
                 parameters = 'parameters',
                 par_name = 'name',
                 par_inherit = 'inherit',
                 code = 'code',
                 root_element = 'simulations',
                 sim_element = 'sim_element',
                 sim_name = 'N')

def find_sim_element(root,sim_name):
    try:
        # searching elements in an xml tree by attributes is available only for
        # Python 2.7+
        return root.find("./"+ _keywords['sim_element'] 
                    +"[@{0}='{1}']".format(_keywords['sim_name'],sim_name))
    except SyntaxError:
        # If the previous line failed then we have to search for element by looping
        # over all the simulation elements
        sim_elements = root.findall("./"+ _keywords['sim_element'])
        for sim_element in sim_elements:
            current_name = sim_element.get(_keywords['sim_name'])
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
        
    for parameter in par_element.findall(_keywords['parameter']):
        par_name = parameter.get(_keywords['par_name'])
        par_value = parameter.text.strip(' \n\t')
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
        parameters[par_name] = par_value
    return parameters

class InvalidNameError(Exception):
    def __str__(self):
        return "The simulation element representing the job must have a name."

class pyGRID:
    
    def __str__(self):
        return '{0}\nParameters: {1}'.format(str(self.sim.args), str(self.parameters))

    def _parse_element(self, sim_element=None):
        """Parse the children of the simulation element and insert them as arguments
        of the cluster job.

        Keyword arguments:
        sim_element -- An ElementTree.Element defining the parameters for
                       the job (default None).
        """
        if sim_element is None:
            return
        
        # the name of the job is expressed as an attribute of the xml element so we deal
        # with it differently 
        job_name = sim_element.get(_keywords['sim_name'])
        if (job_name is None) or (len(job_name) == 0):
            raise InvalidNameError
            return
        self.sim.parse_and_add('-N {0}'.format(job_name))
        
        self.bashFilename = self.sim.args.N + '.sh'
        
        # parse the parameters to pass to the job
        par_element = sim_element.find(_keywords['parameters'])
        if par_element is not None:
            self.parameters = _parse_parameters(par_element)
        
        # parse the remaining qsub options
        for child in sim_element:
        
            if child.tag == _keywords['parameters']:
                continue
        
            argument_value = child.text
            if argument_value is not None:
                argument_value = argument_value.strip(' \n\t')
        
            if child.tag == _keywords['code']:
                self.sim.args.code = argument_value
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
        
        if sim_element is None:
            return
        
        # check if the simulation element inherits from another sim_element
        inherit_from = sim_element.get(_keywords['par_inherit'])
        if inherit_from and parent_map:
            # parse the options from the parent element first
            
            # simulation elements are always the children of the root element so we can
            # use the parent map to retrieve the root
            root_element = parent_map[sim_element]
            # parent_element = root_element.find("./"+ _keywords['sim_element'] +"[@{0}='{1}']".format(_keywords['sim_name'],inherit_from))
            parent_element = find_sim_element(root_element,inherit_from)
            self._parse_element(parent_element)
        
        # parse the element
        self._parse_element(sim_element)
            
    def _generate_param_space(self):
        """Generate all the possible combinations of the parameters for the job.
        Returns a list of parameters and list of all possible combinations of the
        parameters values. If the job has no parameters then returns None for both.
        """
        if len(self.parameters) == 0:
            return None,None
        else:
            return self.parameters.keys(), [x for x in apply(itertools.product, self.parameters.values())]
    
    def submit(self):
        """Submit a job to the queue manager for every possible combination of the
        parameters of the simulation. It also writes an xml file holding the job_id from
        the queue manager for every job submitted with the list of the parameters passed
        and the array information.
        """
        
        # create the bash script first
        self.sim.write_qsub_script(self.bashFilename)
        
        # Root element for the xml holding the information about job submission IDs
        jobs = ET.Element('jobs')
        
        params, combinations = self._generate_param_space()
        if combinations is None:
            # if the simulation doesn't required parameters then self.parameters is empty
            # and results in an empty combinations array
            job = ET.Element('job')
            job.set('name',self.sim.args.N)
            if self.sim.args.t is not None:
                job.set('array',self.sim.args.t)
            
            # submit the job to qsub
            execstring = "qsub -terse "+self.bashFilename
            p = subprocess.Popen(execstring, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
            
            # retrieve the job_id and add it to the job xml element
            jobID = p.stdout.read().strip(' \n\t')
            job.set('id', jobID.split('.')[0])
            jobs.append(job)
        else:
            for c in combinations:
                # define an xml element for this job
                job = ET.Element('job')
                job.set('name',self.sim.args.N)
                if self.sim.args.t is not None:
                    job.set('array',self.sim.args.t)
                
                # generate string of the parameters to be passed to the queue manager
                param_string = []
                for pair in zip(params,c):
                    param_string.append('='.join(str(x) for x in pair))
                    job.set(str(pair[0]),str(pair[1]))
                param_string = ','.join(param_string)
                
                # submit the job to qsub
                execstring = "qsub -terse -v "+param_string+" "+self.bashFilename
                p = subprocess.Popen(execstring, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
                
                # retrieve the job_id and add it to the job xml element
                jobID = p.stdout.read().strip(' \n\t')
                job.set('id', jobID.split('.')[0])
                jobs.append(job)
        # write the xml file with the job IDs
        writeXMLFile(jobs,self.sim.args.N+'.grid')
            

# define the arguments for the python script
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file",help="Specify which file pyGRID should use to load definitions of the simulations")
parser.add_argument("-s", "--simulation",help="The name of the simulation to use")
parser.add_argument("-b", "--submit", action='store_true',help="If submit is specified then pyGRID will submit the job otherwise it will simply create the bash script")

# parse the arguments from the command line
args = parser.parse_args()

# read the xml file, parse it and create the parent map 
tree = ET.parse(args.file)
root = tree.getroot()
parent_map = dict((c, p) for p in root.getiterator() for c in p)

if args.simulation:
    # if the user requested a particular job we create it and submit it
    # matching_sim_element = root.find("./"+ _keywords['sim_element'] +"[@{0}='{1}']".format(_keywords['sim_name'],args.simulation))
    matching_sim_element = find_sim_element(root,args.simulation)
    gridJob = pyGRID(sim_element = matching_sim_element, parent_map = parent_map)
    if args.submit:
        gridJob.submit()
else:
    # otherwise we crate and submit all of them
    for sim_element in root.findall(_keywords['sim_element']):
        gridJob = pyGRID(sim_element = sim_element, parent_map = parent_map)
        if args.submit:
            gridJob.submit()