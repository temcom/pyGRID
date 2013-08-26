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
        sym.parse_and_add('-{0} {1}'.format(child.tag, child.text))
        
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
        print sim.args