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

def writeXMLFile(element,filename):
    rough_string = ET.tostring(element, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    text_file = open(filename, "w")
    text_file.write(reparsed.toprettyxml())
    text_file.close()

def _parse_parameters(par_element = None):
    if par_element is None:
        return
    parameters = dict()
    for parameter in par_element.findall('parameter'):
        par_name = parameter.get('name')
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

class pyGRID:
    
    def __init__(self, sim_element=None):
        self.sim = qsubOptions()
        if sim_element is None:
            return
        self.sim.parse('-N {0}'.format(sim_element.get('N')))
        self.bashFilename = self.sim.args.N + '.sh'
        par_element = sim_element.find('parameters')
        if par_element is not None:
            self.parameters = _parse_parameters(par_element)
        for child in sim_element:
            if child.tag == 'parameters':
                continue
            argument_value = child.text
            if argument_value is not None:
                argument_value = argument_value.strip(' \n\t')
            if child.tag == 'exec':
                self.sim.args.command = argument_value
            elif child.tag == 'pre_code' or child.tag == 'post_code':
                setattr(self.sim.args,child.tag,argument_value)
            else:
                self.sim.parse_and_add('-{0} {1}'.format(child.tag, argument_value))
    
    def _generate_param_space(self):
        if not self.parameters:
            return None, None
        return self.parameters.keys(), [x for x in apply(itertools.product, self.parameters.values())]
    
    def submit(self):
        # create the bash script first
        self.sim.write_qsub_script(self.bashFilename)
        jobs = ET.Element('jobs')
        params, combinations = self._generate_param_space()
        for c in combinations:
            job = ET.Element('job')
            job.set('name',self.sim.args.N)
            if self.sim.args.t is not None:
                job.set('array',self.sim.args.t)
            param_string = []
            for pair in zip(params,c):
                param_string.append('='.join(str(x) for x in pair))
                job.set(str(pair[0]),str(pair[1]))
            param_string = ','.join(param_string)
            execstring = "qsub -terse -v "+param_string+" "+self.bashFilename
            p = subprocess.Popen(execstring, stdout = subprocess.PIPE, stderr = subprocess.STDOUT, shell = True)
            jobID = p.stdout.read().strip(' \n\t')
            job.set('id', jobID.split('.')[0])
            jobs.append(job)
        writeXMLFile(jobs,self.sim.args.N+'.grid')
            

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file")
parser.add_argument("-s", "--simulation")
parser.add_argument("-b", "--submit", action='store_true')
args = parser.parse_args()

tree = ET.parse(args.file)
root = tree.getroot()
if args.simulation:
    sim_element = root.findall("./sim_element[@name='{0}']".format(args.simulation))
    gridJob = pyGRID(sim_element = sim_element.pop())
    if args.submit:
        gridJob.submit()
else:
    for sim_element in root.findall('sim_element'):
        gridJob = pyGRID(sim_element = sim_element)
        if args.submit:
            gridJob.submit()