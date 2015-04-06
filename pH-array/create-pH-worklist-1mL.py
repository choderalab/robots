#!/usr/bin/env python

"""
Create pH worklist to build 1 mL of each pH condition.

"""

# TODO
# * Stage dilution (manually?) of 10 mM stock into DMSO so that we are < 50 uM for final concentrations of erlotinib to avoid solubility problems.
# * Create blanks using DMSO instead of erlotinib stock.

# Solutions to track
# Assume 10 mM bosutinib stock.
solutions = ['citric acid', 'sodium phosphate']
concentrations = { 'citric acid' : 0.1, 'sodium phosphate' : 0.1 } # M
molecular_weights = { 'citric acid' : 192.124, 'sodium phosphate' : 141.96 } # g/mol

# TODO: Replace this taable with a module that computes buffer recipes automatically.
filename = 'citric-phosphate.txt'
infile = open(filename, 'r')
lines = infile.readlines()
infile.close()
conditions = list()
for line in lines:
    # ignore comments
    if line[0] == '#': continue

    # processs data
    elements = line.split()
    entry = dict()
    entry['pH'] = float(elements[0])
    entry['citric acid'] = float(elements[1])
    entry['sodium phosphate'] = float(elements[2])

    # Adjust for 0.1M sodium phosphate.
    entry['sodium phosphate'] *= 2
    total = entry['citric acid'] + entry['sodium phosphate']
    entry['citric acid'] /= total
    entry['sodium phosphate'] /= total

    # Store entry.
    conditions.append(entry)

def aspirate(RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
    return 'A;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def dispense(RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
    return 'D;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def washtips():
    return 'W;\r\n' # queue wash tips

assay_volume = 750.0 # buffer mixture volume (uL)
kinase_volume = 7.5 # kinase stock volume (uL)
buffer_volume = assay_volume - kinase_volume

# Quantity of liquid that clings to outside of tips.
tip_residue_quantity = 3.0 # uL (estimate)

# Track total volume consumed and waste volumes of different solutions.
volume_consumed = dict() # uL
waste_volume = dict() # uL
for solution in solutions:
    volume_consumed[solution] = 0.0
    waste_volume[solution] = 0.0

# Build worklist.
worklist = ""
for loop in range(2):
    for (condition_index, condition) in enumerate(conditions):
        print "pH : %8.1f" % condition['pH']

        # destination well of assay plate
        destination_position = condition_index + 1

        # citric acid
        volume = condition['citric acid']*buffer_volume
        volume_consumed['citric acid'] += volume
        waste_volume['citric acid'] += tip_residue_quantity
        worklist += aspirate('Buffer Components', '5x3 Vial Holder 2015', 1, volume, 1)
        worklist += dispense('Buffer Mixing', '4ti-0136', destination_position, volume, 1)
        worklist += washtips()

        # sodium phosphate
        volume = condition['sodium phosphate']*buffer_volume
        volume_consumed['sodium phosphate'] += volume
        waste_volume['sodium phosphate'] += tip_residue_quantity
        worklist += aspirate('Buffer Components', '5x3 Vial Holder 2015', 2, volume, 2)
        worklist += dispense('Buffer Mixing', '4ti-0136', destination_position, volume, 2)
        worklist += washtips()

# Write worklist.
worklist_filename = 'ph-worklist.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(worklist)
outfile.close()

# Report total volumes.
print "citric acid:      %10.3f uL" % volume_consumed['citric acid']
print "sodium phosphate: %10.3f uL" % volume_consumed['sodium phosphate']
print ""

# Compute waste quantities.
waste_quantity = dict() # quantity, in mg
for solution in solutions:
    waste_quantity[solution] = (waste_volume[solution] * 1e-6) * concentrations[solution] * molecular_weights[solution] # g

# Report estimates of waste volumes.
print "citric acid:      %10.3f uL (%8.3f mg)" % (waste_volume['citric acid'], waste_quantity['citric acid'] * 1e3)
print "sodium phosphate: %10.3f uL (%8.3f mg)" % (waste_volume['sodium phosphate'], waste_quantity['sodium phosphate'] * 1e3)
print ""
