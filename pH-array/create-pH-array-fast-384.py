#!/usr/bin/env python

"""
Create pH arrays along rows of 384-well plate.

Optimized for speed.
"""

# TODO: Replace this taable with a module that computes buffer recipes automatically.
filename = 'citric-phosphate-24.txt'
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
    if (volume > 1000.0):
        raise Exception("Aspirate volume > 1000 uL (asked for %.3f uL)" % volume)
    return 'A;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def dispense(RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
    if (volume > 1000.0):
        raise Exception("Dispense volume > 1000 uL (asked for %.3f uL)" % volume)
    return 'D;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def washtips():
    return 'W;\r\n' # queue wash tips

assay_volume = 80.0 # assay volume (uL)
buffer_volume = assay_volume
assay_RackType = '4ti-0264' # black 384-well plate with clear bottom

volume_consumed = dict()
volume_consumed['citric acid'] = 0.0
volume_consumed['sodium phosphate'] = 0.0

# Build worklist.
worklist = ""

class TransferQueue(object):
    def __init__(self, SourceRackLabel, SourceRackType, SourcePosition, tipmask):
        self.SourceRackLabel = SourceRackLabel
        self.SourceRackType = SourceRackType
        self.SourcePosition = SourcePosition
        self.tipmask = tipmask
        self.worklist = ""
        self.cumulative_volume = 0.0
        self.MAX_VOLUME = 950.0
        self.queue = list()
        return

    def transfer(self, DestRackLabel, DestRackType, DestPosition, volume):
        if (self.cumulative_volume + volume > self.MAX_VOLUME):
            self._flush()
        item = (DestRackLabel, DestRackType, DestPosition, volume)
        self.queue.append(item)
        self.cumulative_volume += volume

    def _flush(self):
        self.worklist += aspirate(self.SourceRackLabel, self.SourceRackType, self.SourcePosition, self.cumulative_volume + 0.01, self.tipmask)
        for item in self.queue:
            (DestRackLabel, DestRackType, DestPosition, volume) = item
            self.worklist += dispense(DestRackLabel, DestRackType, DestPosition, volume, self.tipmask)
        self.worklist += washtips()
        # Clear queue.
        self.queue = list()
        self.cumulative_volume = 0.0

    def write(self):
        self._flush()
        return self.worklist

citric_acid_queue = TransferQueue('0.1M Citric Acid', 'Trough 100ml', 1, 1)
sodium_phosphate_queue = TransferQueue('0.1M Sodium Phosphate', 'Trough 100ml', 2, 2)

nrows = 16 # number of rows to generate

# Build worklist.
worklist = ""
for row_index in range(nrows):
    print "Row %d :" % row_index
    for (condition_index, condition) in enumerate(conditions):
        # destination well of assay plate
        destination_position = 12 * condition_index + row_index + 1
        if (destination_position > 384):
            raise Exception("destination position out of range (%d)" % destination_position)

        print "  well %3d : pH : %8.1f" % (destination_position, condition['pH'])

        # citric acid
        volume = condition['citric acid']*buffer_volume
        volume_consumed['citric acid'] += 2*volume
        citric_acid_queue.transfer('Assay Plate', assay_RackType, destination_position, volume)

        # sodium phosphate
        volume = condition['sodium phosphate']*buffer_volume
        volume_consumed['sodium phosphate'] += 2*volume + 1
        sodium_phosphate_queue.transfer('Assay Plate', assay_RackType, destination_position, volume)

    worklist += citric_acid_queue.write()
    worklist += sodium_phosphate_queue.write()

# Write worklist.
worklist_filename = 'ph-worklist-fast-384.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(worklist)
outfile.close()

# Report total volumes.
print "citric acid:      %8.3f uL" % volume_consumed['citric acid']
print "sodium phosphate: %8.3f uL" % volume_consumed['sodium phosphate']
