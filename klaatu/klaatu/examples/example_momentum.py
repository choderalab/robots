'''
Created on 25.04.2014

@author: jan-hendrikprinz
'''

if __name__ == '__main__':
    pass

# from momentum.momentum2xml import Momentum, PyToMomentum

from components.momentum.momentum import Momentum
from util.xmlutil import XMLWrap
#from momentum.templates import evo_run_singleplate, flow_if, flow_iteration_assign
#import momentum.converter as cv
import copy

from lxml import etree, objectify
    
# print cv.xml_to_python(cv.momentum_to_xml(source))

# create a psr object fom a Momentum source file, readXML is also possible although this is my own XML specification
# and is mainly used as an intermediate step to parse into a python object

psr = Momentum.readMomentum("components/momentum/templates/process/plAnalysis.mpr")

# example_tecan change a property inside the python object tree. A next level can be specified using a "/" separated string
# if the level is a dict than it ust picks the value with the given key, in case of a list of dicts it picks the entry which has
# an 'id' key with the given value for lists also a number can be given with specifies the index
# this is meant to be similar to an xpath for XML but is less powerful. At some point we might use xpath only and edit the 
# XML elemtns directly 

# psr['profile/devices/BarCode/params/Active'] = 'Inactive'

# copy (shallow) and insert the first process step at position 2 twice. Note that process steps to NOT have an ID attribute

# psr['process/steps'].insert(2, psr['process/steps/0'])
# psr['process/steps'].insert(2, psr['process/steps/0'])
# psr['process/steps'].insert(2, evo_run_singleplate('script.msc', 'MyPlate', 'left(1)', 'left(2)'))

# inserts at the beginning (0) an if construct with the evo script run in two configurations
# the functions flow_if and evo_run_singleplate, etc. are just factories for specific python objects that correspond to the description of a
# particular command for momentum

#psr['process/steps'].insert(0, 
#                               flow_if('Iteration>4',
#                                       evo_run_singleplate('script.msc', 'MyPlate', 'left(1)', 'left(2)'),
#                                       evo_run_singleplate('script.msc', 'OtherPlate', 'right(1)', 'right(1)')
#                                       )
#                               )

# extract the plate IDs from the script

wp = XMLWrap('momentum')
print wp.xml_as_py( psr.asXML() )

plateIDs = [ psr['id'] for psr in psr['process/containers'] ]

# print plateIDs

# copy the first three steps in the processlist

temp = psr['process/steps'][0:3]

# clear the list if processes

psr['process/steps'] = []

# loop over plates

for psr in plateIDs:
    
    # copy the first container description the the first step in the template
    cont = temp[0]['containers'][0]
    
    # replace the id in the container to make it use another plateID
    cont['id'] = psr
    
    # replace the list of containers by a list that contains only the first element (could be more)    
    temp[0]['containers'] = [cont] 
    
    # make a deep copy of the three step template and add it to the momentum script. Deepcopy is necessary, otherwise the changes in the template
    # would be present in all templates. This might be a desired feature in another case but here it is not 
    psr['process/steps'].extend(copy.deepcopy(temp))
    


# create an if cascade that assignes different strings to the varible 'PlateType' in iterations 1 to 8 like Muniz explained
# NOTE : Momentum does not allow more than 8 iterations!!!

# psr['process/steps'].insert(0, flow_iteration_assign('PlateType', [1,8], ['"A"', '"B"', '"C"', '"D"', '"E"', '"F"', '"G"', '"H"']))

# finally write the modified script to a file for Momentum to import
#psr.toMomentumFile("example_momentum_worklist.txt")

# Read a momentum process .mpr file and convert it into xmlutil
psr = Momentum.readMomentum("components/momentum/templates/process/plAnalysis.mpr")
xml= psr.asXML()
xml = etree.tostring(objectify.fromstring(xml), pretty_print = True)
print xml

psr = Momentum.fromXML(xml)

print psr.asMomentum()