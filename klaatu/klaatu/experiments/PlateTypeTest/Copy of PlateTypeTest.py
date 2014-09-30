#!/usr/bin/env python

###############################################################################
##
##                    TECAN EVO WORKLIST GENERATOR
##
##                          tecanerator V 0.3
##
##   Authors:               Sonya Hanson
##                          Jan-Hendrik Prinz
##                          John D. Chodera
##
###############################################################################


# March 28, 2014 Jan-Hendrik Prinz and Sonya Hanson play with robot.
# Set up triplicates of Src-Bosutinib binding assay in 5 different plate types.
# Updated with full plate types. March 31, 2014.
# Added classes for objects used in pipetting
# Apr 15th fixed first running version with classes

# TODO:
# Add documentation !!!!!!!!!!!!!!!!!!!!!!
# Add dispense schemes to compute estimates of accuracies
# Add detailed output for plate definition in some kind of XML format containing amounts and errors
# Add Advances WL commands to Worklist
# Think about use of Units, maybe switch to other units package
# Clean up parsing stuff in util.Parser
# Clean up WellSet, Well using util.Place

from components.momentum.momentum import Parser
from components.tecan import Plate, Worklist, Source, Mixture, Scheduler, V
import copy

import xmlPythonize.xmlPy as xp


################################################################################
##  READ
################################################################################

parser = Parser.readMomentum("components/momentum/templates/process/plAnalysis.mpr")

plates = [ p for p in parser['process/containers'] ]
plateIDs = [ p['id'] for p in plates ]
momentumPlateTypes = [ p['params']['ContainerTypeNameId'] for p in plates ]

################################################################################
##  SOURCE PLATE DEFINITIONS
################################################################################

source_plate = Plate({ 'label' : 'Source', 'racktype' : '5x3 Vial Holder' })


################################################################################
##  TARGET PLATE DEFINITIONS
################################################################################

plate_test_types = {
    '96F' : Plate({ 'label' : '96wellFull',   'racktype' : '', 'dimensions' : [8,12] }),
    '96H' : Plate({ 'label' : '96wellHalf',   'racktype' : '', 'dimensions' : [8,12] }),
    '384' : Plate({ 'label' : '384wellFull',  'racktype' : '', 'dimensions' : [16,24] })
}


################################################################################
##  SOURCE WELL DEFINITIONS
################################################################################

source_protein_L = Source({
    'description' : 'Protein Low C',
    'label' : 'Protein_Low',
    'plate' : source_plate,
    'mixture' : Mixture({ 
        'Protein_L' : '100%'
    }),
    'volume' : '10ml',
    'well' : 'A1'
    }
)

source_protein_H = Source({
    'description' : 'Protein High C',
    'label' : 'Protein_High',
    'plate' : source_plate,
    'mixture' : Mixture({ 
        'Protein_H' : '100%'
    }),
    'volume' : '10ml',
    'well' : 'B1'
    }
)

source_buffer = Source({
    'description' : 'Buffer Solution',
    'label' : 'Buffer',
    'plate' : source_plate,
    'mixture' : Mixture({ 
        'Buffer' : '100%'
    }),
    'volume' : '10ml',
    'well' : 'C1'
    }
)

sources = [source_protein_L, source_protein_H, source_buffer ]

################################################################################
##  TARGET WELL DEFINITION BY RULES
################################################################################

# plate rules can contain 'wells' and 'target' to specify for which something is set 
# 'mixture' specifies the mixture as a dictionary of the liquid : concentration in Molar or %
# 'volume' species the desired target volume of the liquid

plate_rules = [
    { 'wells': 'A,C,E:1-12', 'mixture' : { 'Protein_H' : '100%'} },
    { 'wells': 'B,D,F:1-12', 'mixture' : { 'Protein_L' : '100%'} },
    { 'wells': 'G:1-12', 'mixture' : { 'Buffer' : '100%'} },
    { 'target' : '96wellFull*', 'wells' : 'A-G:1-12', 'volume' : '75ul'},
    { 'target' : '96wellHalf*', 'wells' : 'A-G:1-12', 'volume' : '35ul'},
    { 'target' : '384wellFull*', 'wells' : 'A-G:1-12', 'volume' : '20ul'}
]

for (id, target) in plate_test_types.iteritems():
    target.apply_rule(plate_rules)

################################################################################
##  GENERATE SCHEDULER USING SOURCES, TARGETS AND RULES
################################################################################

evo_filenames = {}

for (id, plate) in plate_test_types.iteritems():
        
    sc = Scheduler(sources, [ plate ])
    sc.generate()

# apply a list of rules to specify the usage of the heads
# usually things that are similar in rows should be dispensed using row, while col wise things should be used with free

    task_rules = [ 
                  { 'source' : '', 'head' : '1-7', 'assignment' : 'row' },
                 ]

    sc.apply_rule(task_rules)

    # Build worklist generator
    wl = Worklist()

    # Write scheduled tasks to worklist
    sc.write_to_worklist(wl)

    worklist_filename = 'plate_types-worklist-' + plate.label + '.gwl'
    evo_filenames[id] = worklist_filename
    outfile = open(worklist_filename, 'w')
    outfile.write(wl.script)
    outfile.close()

    # Report
    
    print "\nReport for : " + plate.label

    print
    print "Dispense Actions"
    
    
    for index in range(1,9):
        print "head", index, " aspirates : ", sc.dispense_volumes[index],'total : ', sum(sc.dispense_volumes[index])
     
    print
    print "Used liquids"
    
    for (source_index, source) in enumerate(sources):
        if sc.volume_consumed[source.label] > 0.0:
            print "{:<20s}:       {:.3f} uL of {:.3f} uL ".format( source.label, sc.volume_consumed[source.label], V(source.volume).val('u'))
           
            
    print "System Liquid (max) :        {:.3f} uL".format( (wl.used_system_liquid()).val('u'))
    
    print
    print "Performed Actions"
    
    print "Aspirations:           %(number)4d" % { 'number' : wl.aspirations}
    print "Dispenses:             %(number)4d" % { 'number' : wl.dispenses}
    print "Washs (max):           %(number)4d" % { 'number' : wl.washs}
    
        
# Infinite

s = ''
with open ('infinite_temp.xml', "r") as myfile:
    s = myfile.read()

s = s.replace('tecan.at.schema.documents', '')
wr = xp.XMLPyWrap('container')
oo = wr.xml_as_py(s)

infiniteTypeFileName = { 
                'ActivePlate' : 'Corning 3679 Half-Area UV-transparent clear bottom',
                'Corning3569' : 'Corning 3679 Half-Area UV-transparent clear bottom',
                'Corning3671' : 'Corning 3679 Half-Area UV-transparent clear bottom' 
                }

# print oo

for p in plateIDs:
#    print oo['TecanMeasurement/MeasurementManualCycle/CyclePlate/file']
    dict(oo['TecanMeasurement/MeasurementManualCycle/CyclePlate'])['file'] = infiniteTypeFileName[p]
    
    xml = wr.py_as_xml(oo)
    
    worklist_filename = 'infinite-worklist-' + p + '.infi'
    
    outfile = open(worklist_filename, 'w')
    outfile.write(xml)
    outfile.close()


temp = parser['process/steps'][0:3]

# clear the list if processes

parser['process/steps'] = []

# loop over plates

plateTypeByID = {
                 'ActivePlate' : '96H',
                 'Corning3569' : '96F',
                 'Corning3671' : '384'
                 }

for p in plateIDs:
    # copy the first container description the the first step in the template
    cont = temp[0]['containers'][0]
    
    # replace the id in the container to make it use another plateID
    cont['id'] = p
    temp[0]['params']['ScriptName'] = evo_filenames[plateTypeByID[p]]
    
    # replace the list of containers by a list that contains only the first element (could be more)    
    temp[0]['containers'] = [cont] 
    
    # ADD INIFINITE SCRIPT
    
    # make a deep copy of the three step template and add it to the momentum script. Deepcopy is necessary, otherwise the changes in the template
    # would be present in all templates. This might be a desired feature in another case but here it is not 
    parser['process/steps'].extend(copy.deepcopy(temp))
    


# create an if cascade that assignes different strings to the varible 'PlateType' in iterations 1 to 8 like Muniz explained
# parser['process/steps'].insert(0, flow_iteration_assign('PlateType', [1,8], ['"A"', '"B"', '"C"', '"D"', '"E"', '"F"', '"G"', '"H"']))

# finally write the modified script to a file for Momentum to import
parser.toMomentumFile("PlateTypeTest.txt")

# Copy all files to appropriate locations
# Import momentum file and create experiment
# GO