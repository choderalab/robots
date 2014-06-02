#!/usr/bin/env python

# Create pH array (with no compound) with symmetric "blanks"
# Optimized for speed.
 
# TODO
# * Stage dilution (manually?) of 10 mM stock into DMSO so that we are < 50 uM for final concentrations of erlotinib to avoid solubility problems.
# * Create blanks using DMSO instead of erlotinib stock.

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

assay_volume = 100.0 # assay volume (uL)
buffer_volume = assay_volume
assay_RackType = 'Corning 3651' # black with clear bottom
assay_RackType = 'Corning 3679' # uv-transparent half-area

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
    
citric_acid_queue = TransferQueue('Source Plate', '4x3 Vial Holder', 1, 1)
sodium_phosphate_queue = TransferQueue('Source Plate', '4x3 Vial Holder', 2, 2)

for (condition_index, condition) in enumerate(conditions):
    print "pH : %8.1f" % condition['pH']

    # destination well of assay plate
    destination_position = condition_index + 1

    # citric acid
    volume = condition['citric acid']*buffer_volume
    volume_consumed['citric acid'] += 2*volume 
    citric_acid_queue.transfer('Assay Plate', assay_RackType, destination_position, volume)
    citric_acid_queue.transfer('Assay Plate', assay_RackType, 96 - destination_position + 1, volume)

    # sodium phosphate
    volume = condition['sodium phosphate']*buffer_volume
    volume_consumed['sodium phosphate'] += 2*volume + 1
    sodium_phosphate_queue.transfer('Assay Plate', assay_RackType, destination_position, volume)
    sodium_phosphate_queue.transfer('Assay Plate', assay_RackType, 96 - destination_position + 1, volume)

worklist = ""
worklist += citric_acid_queue.write()
worklist += sodium_phosphate_queue.write()

# Write worklist.
worklist_filename = 'ph-worklist.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(worklist)
outfile.close()

# Report total volumes.
print "citric acid:      %8.3f uL" % volume_consumed['citric acid']
print "sodium phosphate: %8.3f uL" % volume_consumed['sodium phosphate']
