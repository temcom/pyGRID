#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Aug 23 19:45:20 2013

@author: Jacopo Sabbatini
"""

import argparse
import xml.etree.ElementTree as ET
from pyqsub import qsubOptions

def simulation(sym_element=None):
    sym = qsubOptions()
    if sym_element is None:
        return sym
    sym.parse('-N {0}'.format(sym_element.get('N')))
    
    for child in sym_element:
        argument_value = child.text
        if argument_value is not None:
            argument_value = argument_value.strip(' \n\t')
        if child.tag == 'exec':
            sym.args.command = argument_value
        elif child.tag == 'pre_code' or child.tag == 'post_code':
            setattr(sym.args,child.tag,argument_value)
        else:
            sym.parse_and_add('-{0} {1}'.format(child.tag, argument_value))
        
    return sym

parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file")
parser.add_argument("-s", "--simulation")
args = parser.parse_args()

tree = ET.parse(args.file)
root = tree.getroot()
if args.simulation:
    sym = root.findall("./sym[@name='{0}']".format(args.simulation))
    sim = simulation(sym.pop())
    print sim.args
else:
    for sym in root.findall('sym'):
        sim = simulation(sym)
        filename = sim.args.N + '.sh'
        sim.write_qsub_script(filename, echo = True)
        print sim.args