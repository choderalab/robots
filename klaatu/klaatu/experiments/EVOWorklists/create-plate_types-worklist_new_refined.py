#!/usr/bin/env python

###############################################################################
##
##                    TECAN EVO WORKLIST GENERATOR
##
##                                 V 0.1
##
###############################################################################

# March 28, 2014 Jan-Hendrik Prinz and Sonya Hanson play with robot.
# Set up triplicates of Src-Bosutinib binding assay in 5 different plate types.
# Updated with full plate types. March 31, 2014.
# Added classes for objects used in pipetting


###############################################################################        
##  WORKLIST FUNCTION WRITER
###############################################################################

def aspirate(RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
    global aspirations
    aspirations += 1
    return 'A;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def dispense(RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
    global dispenses
    dispenses += 1
    return 'D;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)

def washtips():
    return 'W;\r\n' # queue wash tips

###############################################################################        
##  ROW / COL DEFIINITION UTILITY FUNCTIONS
###############################################################################

# well definitions

size96 = [8, 12]
size384 = [16, 24]

def WellToPosition(size, well):
    h = size[0]
    w = size[1]
    return [(well - 1) % h + 1, (well - 1) // h + 1]

def PositionToWell(size, pos):
    h = size[0]
    w = size[1]
    return (pos[0] - 1) * h + pos[1]    

def PositionToName(size, pos):
    h = size[0]
    w = size[1]
    return chr(64 + pos[0]) + str(pos[1])

def NameToPosition(size, str):
    return [ord(str[0]) - 64, int(str[1:])]

def WellToName(size, well):
    return PositionToName(size, WellToPosition(size,well))

def NameToWell(size, str):
    return PositionToWell(size, NameToPosition(size, str))

def Wells(size, row=None, col=None, well=None):
    h = size[0]
    w = size[1]
    n = h * w

# Wells(size96, row: ['A', 'C', 'E'], col: 'all', well: [[1, 2] ,[10, 2]] )

def allWells(size, order='row'):
    rows = size[0]
    cols = size[1]
    if order == 'row':
        return [[row,col] for row in range(1,rows + 1) for col in range(1,cols + 1)]
    else:
        return [[row,col] for col in range(1,cols + 1) for row in range(1,rows + 1) ]

def _interprete_row(el):
    if type(el) is int:
        return el
    else:
        return ord(el) - 64
    
def _interprete_well(el, size=size96):
    if type(el) is int:
        return WellToPosition(size, el)
    if type(el) is list:
        return el
    else:
        return NameToPosition(size,el)
    
def filter(list, rows=None, cols=None, wells=[]):
    if rows is None:
        rows = range(1,17)
    
    if cols is None:
        cols = range(2,25)
            
    rows = [ _interprete_row(el) for el in rows ]

    return [
        el for el in list 
        if ((el[0] in rows) and (el[1] in cols)) or (el in wells) 
        ]
    
rowA = dict([ ( chr(64 + r), range(r, 97, 8)) for r in range(1,9) ] + [ (r, range(r, 97, 8)) for r in range(1,9) ])
row = [ range(r, 97, 8) for r in range(1,9) ]
colA = dict([ (r, range((r - 1)*8 + 1, (r - 1)*8 + 9)) for r in range(1,13) ])
col = [ range((r - 1)*8 + 1, (r - 1)*8 + 9) for r in range(1,13) ]
    

###############################################################################        
##  CLASS DEFINITIONS - not used yet
###############################################################################

# This is to decorate strings the contain liquid names to make sure only valid liquid names are used.  
class Liquid:
    'A liquid is named fluid that is to be transported from one'    
    def __init__(self, name):
        self.name = name

# Contains the specific mixture of liquid types with their conentrations. The volume is not stored and is a property of a job or a well.
class Mixture:
    'A mixture is a description for a combination of one or more liquids with their respective concentrations'
    def __init__(self, type):
        self.type = ''
        self.wells = 0
        self.label = ''
        self.name = ''
        self.liquids = [];
        self.concentration = [];

#  The Plate contains the information necessary to bind to the EvoSoftware and refer to the objects on the deck of the robot.
class Plate:
    'A plate is a movable location that can contain wells'
    def __init__(self, type='', dimensions = size96, name = '', label = '', description = ''):
        self.type = type
        self.label = label
        self.name = name
        self.description = description
        self.dimensions = dimensions
        
    def wells(self):
        return WellSet([
            Well(position=el, plate=self) for el in allWells(self.dimensions)
            ])
        return WellSet(allWells(self.dimensions));
        
    def __hash__(self):
        return hash(self.label)
        
    def __eq__(self, other):
        # Two wells are considered the same, if the plate is the same and the position
        if isinstance(other, self.__class__):
            return (self.label == other.label)
        else:
            return False

# Jobs are the objects containing all information for a specific command for the robot. These are then to be parsed into a worklist.
class Job:
    'A job is a command to be carried out by the Liquid Handling Robot'
    def __init__(self,):
        self.type = ''
        return self

# Defines a location on a plate with a specific filling volume and a mixture. Some wells are sources and some are destinations in the pipetting process.
# The necessary pipetting jobs are to be computed by the program including (almost) optimal use of the dispense heads available.

class Well:
    'A well is a liquid holding site on a plate'   
    def __init__(self, plate='', name='', position=[1,1], content=[]):
        self.position = _interprete_well(position)
        self.content = content
        self.plate = plate        

    def set_plate(self, plate):
        self.plate = plate
        
    def __hash__(self):
        return hash(self.position[0]) ^ hash(self.position[1]) ^ hash(self.plate)
        
    def __eq__(self, other):
        # Two wells are considered the same, if the plate is the same and the position
        if isinstance(other, self.__class__):
            return (self.position == other.position and self.plate == other.plate)
        else:
            return False
        
class WellSet(list):
    'A WellSet is a set of wells on one or more plates'
    
    def position_list(self):
        return [ el.position for el in self ]
    
    def filter(self, rows=None, cols=None, wells=[]):
        if rows is None:
            rows = range(1,17)
    
        if cols is None:
            cols = range(1,25)
            
        rows = [ _interprete_row(el) for el in rows ]

        return WellSet([
                el for el in self if ((el.position[0] in rows) and (el.position[1] in cols)) or (el.position in wells) 
                ])
            
ws = Plate(dimensions=[3,5], name='Corning 3651').wells().filter(cols=range(2,5))

print ws.position_list()
print ws[0].plate.name
print len(ws.filter(rows=[1]))




# Ideas that would be cool, if they worked   
# sPlate1 = new Plate()
# sPlate1.wells('rows: A,C,E').set( new Mixture( [ 'Buffer : 75%, DMSO: 25%' ] ))
# sPlate1.wells('rows: A,C,E').set( new Mixture( [ 'Buffer : 75%, DMSO: 25%' ] ))

###############################################################################        
##  PLATE DEFINITIONS
###############################################################################
    
# Destination Plate Definitions
    
destination_plate_1 = {
    'label' : 'Corning3651',
    'racktype' : 'Corning 3651',
    'total_volume' : 75,
    'dimensions' : [8, 12],
    'wells' : 96,
    'maximum_volume' : 100,
    'well_shift' : 0
}

destination_plate_2 = {
    'label' : '96well-UVStar',
    'racktype' : '96 Well Microplate',
    'total_volume' : 75,
    'dimensions' : [8, 12],
    'wells' : 96,
    'maximum_volume' : 100,
    'well_shift' : 0
}

destination_plate_3 = {
    'label' : 'Corning3679',
    'racktype' : 'Corning 3679',
    'total_volume' : 50,
    'dimensions' : [8, 12],
    'wells' : 96,
    'maximum_volume' : 50,
    'well_shift' : 0
}

destination_plate_4 = {
    'label' : '384well',
    'racktype' : '384 Well Plate',
    'total_volume' : 20,
    'dimensions' : [16, 24],
    'wells' : 384,
    'maximum_volume' : 20,
    'well_shift' : 12*16
}

destination_plate_5 = {
    'label' : '384well2',
    'racktype' : '384 Well Plate',
    'total_volume' : 20,
    'dimensions' : [16, 24],
    'wells' : 384,
    'maximum_volume' : 20,
    'well_shift' : 12*16
}

destination_plate_6 = {
    'label' : '384well3',
    'racktype' : '384 Well Plate',
    'total_volume' : 20,
    'dimensions' : [16, 24],
    'wells' : 384,
    'maximum_volume' : 20,
    'well_shift' : 12*16
}

# NOT USED PLATES

destination_plate_X = {
    'label' : '96well4ti',
    'racktype' : '96 Well Microplate',
    'total_volume' : 100,
    'dimensions' : [8, 12],
    'wells' : 96,
    'maximum_volume' : 100,
    'well_shift' : 0
}

# destination_plate_list = [ destination_plate_4 ]

destination_plate_list = [ destination_plate_1, destination_plate_2, destination_plate_3, destination_plate_4, destination_plate_5, destination_plate_6]


# Source Definitions

source_protein_L = {
    'name' : 'Protein Low Concentration',
    'short' : 'Protein_Low',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 1,
}

source_protein_H = {
    'name' : 'Protein High Concentration',
    'short' : 'Protein_High',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 2,
}

source_protein_L_Old = {
    'name' : 'Protein (OLD) Low Concentration',
    'short' : 'Protein_Low_Old',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 4,
}

source_protein_H_Old = {
    'name' : 'Protein (OLD) High Concentration',
    'short' : 'Protein_High_Old',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 5,
}

source_buffer = {
    'name' : 'Buffer',
    'short' : 'Buffer',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 3,
}

source_bosutinib_list = [
    {
        'name' : 'Bosutinib #' + str( no ),
        'short' : 'Bosutinib_' + str( no ),
        'label' : 'Bosutinib',
        'racktype' : '96 well DeepWell 4ti-0136',
        'well' : (no - 1) * 8 + 1,
    } for no in range(1,13)
]

source_list = [source_protein_L, source_protein_H, source_buffer ] + source_bosutinib_list

task_buffer = [{
    'source' : source_buffer,
    'destination' : destination,
    'percentage' : 1.00,
    'destination_wells' : range(7, 97, 8),
    'head' : 64
} for destination in destination_plate_list]

task_protein_L = [ {
    'source' : source_protein_L,
    'destination' : destination,
    'percentage' : 1.00,
    'destination_wells' : range((head - 1) * 2 + 1, 97, 8),
    'head' : 2**((head - 1)*2)
} for head in range(1,4) for destination in destination_plate_list]

task_protein_H = [ {
    'source' : source_protein_H,
    'destination' : destination,
    'percentage' : 1.00,
    'destination_wells' : range((head - 1) * 2 + 2, 97, 8),
    'head' : 2**((head - 1)*2 + 1)
} for head in range(1,4) for destination in destination_plate_list]

task_bosutinib_list = [ {
    'source' : source_bosutinib_list[no - 1],
    'destination' : destination,
    'percentage' : 0.25,
    'destination_wells' : range((no - 1) * 8 + 1, (no - 1) * 8 + 8),
    'head' : 2**((no - 1) % 6)
} for no in range(1,13) for destination in destination_plate_list]

task_list = task_protein_L + task_protein_H + task_buffer

# construct list of consumed solutions (reagents) used
volume_needed = dict()
volume_dispenses = dict()

for solution in source_list:
    volume_needed[solution['short']] = 0.0
    
# construct list of consumed solutions (reagents) used
volume_consumed = dict()
for (solution_index, solution) in enumerate(source_list):
    volume_consumed[solution['short']] = 0.0
    
# Maximum possible aspiration volume per head
maximum_dispense_level = 900.0
maximum_head_number = 8

# Fast pipetting
do_fast_pipetting = True

# Number of Aspirations and Dispensings
aspirations = 0
dispenses = 0

# Build worklist.
worklist = ""

# Running state of the head
dispense_volumes = [[] for p in range(1, 257)]
loaded_volume = [0.0 for p in range(1, 257)]
loaded_source = ['' for p in range(1, 257)]

for (task_index, task) in enumerate(task_list):
    source = task['source']
    destination = task['destination']
    volume = task['percentage'] * destination['total_volume']
    head = task['head']
    
    if loaded_source[head] == '':
        loaded_source[head] = source['short']
    
    for (destination_well_index, destination_well) in enumerate(task['destination_wells']):
        volume_needed[source['short']] += volume   
        loaded_volume[head] += volume
        if (loaded_volume[head] > maximum_dispense_level) or (source['short'] != loaded_source[head]):
            loaded_source[head] = source['short']
            # aspirate as much as possible
            dispense_volumes[head].append( loaded_volume[head] - volume )
            loaded_volume[head] = volume
                                                            
for index in range(1,8):
    dispense_volumes[2**(index - 1)].append( loaded_volume[2**(index - 1)] )
    loaded_volume[2**(index - 1)] = 0.0
    
# dispense

for index in range(1,8):
    print index," aspirates : ", dispense_volumes[2**(index - 1)]
    

dispense_index = [0 for p in range(1, 257)]

first_aspirate = True

for (task_index, task) in enumerate(task_list):
    source = task['source']
    destination = task['destination']
    volume = task['percentage'] * destination['total_volume']
    head = task['head']
    
    for (destination_well_index, destination_well) in enumerate(task['destination_wells']):      
        if do_fast_pipetting:
            if loaded_volume[head] < volume:
                # aspirate as much as possible
                if loaded_volume[head] != 0.0:
                    print "Non empty head washed !!!! Unneccessary"
                    print loaded_volume[head]

                loaded_volume[head] = 0.0
                if not first_aspirate:                    
                    worklist += washtips()
                first_aspirate = False
                
                possible_volume = dispense_volumes[head][dispense_index[head]]
                dispense_index[head] += 1
                
                volume_needed[source['short']] -= possible_volume
                loaded_volume[head] += possible_volume                
                                
                worklist += aspirate(source['label'], source['racktype'], source['well'], possible_volume, head)
    
            if destination['wells']==384:
                destination_well = (destination_well - 1) % 8 + ((destination_well - 1) // 8) * 16 + 1
                destination_well += destination['well_shift']

            if not do_fast_pipetting:
                loaded_volume += volume
                worklist += aspirate(source['label'], source['racktype'], source['well'], volume, head)

            worklist += dispense(destination['label'], destination['racktype'], destination_well, volume, head)
            loaded_volume[head] -= volume
            volume_consumed[source['short']] += volume

            if not do_fast_pipetting:
                loaded_volume[head] = 0.0
                worklist += washtips()
    
worklist_filename = 'plate_types-worklist-protein_new-final.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(worklist)
outfile.close()

# Report total volumes needed.
for (solution_index, solution) in enumerate(source_list):
    print "%(name)s:         %(volume)8.3f uL" % { 'name' : solution['name'], 'volume' : volume_needed[solution['short']]}

# Report total volumes.
for (solution_index, solution) in enumerate(source_list):
    print "%(name)s:         %(volume)8.3f uL" % { 'name' : solution['name'], 'volume' : volume_consumed[solution['short']]}

for index in range(1,8):
    print "%(head)s:         %(volume)8.3f uL" % { 'head' : index, 'volume' : loaded_volume[2**(index - 1)]}
    

print "Aspirations:  %(number)4d" % { 'number' : aspirations}
print "Dispenses:    %(number)4d" % { 'number' : dispenses}
