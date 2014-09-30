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

# This is to decorate strings the contain liquid names to make sure only valid liquid names are used.  
class Liquid:
    'A liquid is named fluid that is to be transported from one'    
    def __init__(self, name):
        self.name = name

###############################################################################        
##  CLASS DEFINITIONS - not used yet
###############################################################################

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
    def __init__(self, type):
        self.type = ''
        self.wells = 0
        self.label = ''
        self.name = ''
        self.description = ''
        self.dimensions = [ 8, 12 ]
        
    def wells(self):
        return self.wells;

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
    def __init__(self, name):
        self.name = name

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
    'total_volume' : 100,
    'dimensions' : 96
}

destination_plate_2 = {
    'label' : 'Corning3679',
    'racktype' : 'Corning 3679',
    'total_volume' : 50,
    'dimensions' : 96
}

destination_plate_3 = {
    'label' : '96well4ti',
    'racktype' : '96 Well Microplate',
    'total_volume' : 100,
    'dimensions' : 96
}

destination_plate_4 = {
    'label' : '384well',
    'racktype' : '384 Well Plate',
    'total_volume' : 20,
    'dimensions' : 384
}

destination_plate_5 = {
    'label' : '96well-UVStar',
    'racktype' : '96 Well Microplate',
    'total_volume' : 100,
    'dimensions' : 96
}

destination_plate_list = [ destination_plate_1, destination_plate_2, destination_plate_3, destination_plate_4, destination_plate_5]


# well definitions

rowA = dict([ ( chr(64 + r), range(r, 97, 8)) for r in range(1,9) ] + [ (r, range(r, 97, 8)) for r in range(1,9) ])
row = [ range(r, 97, 8) for r in range(1,9) ]
colA = dict([ (r, range((r - 1)*8 + 1, (r - 1)*8 + 9)) for r in range(1,13) ])
col = [ range((r - 1)*8 + 1, (r - 1)*8 + 9) for r in range(1,13) ]

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
    'percentage' : 0.75,
    'destination_wells' : range(7, 97, 8),
    'head' : 64
} for destination in destination_plate_list]

task_protein_L = [ {
    'source' : source_protein_L,
    'destination' : destination,
    'percentage' : 0.75,
    'destination_wells' : range((head - 1) * 2 + 1, 97, 8),
    'head' : 2**((head - 1)*2)
} for head in range(1,4) for destination in destination_plate_list]

task_protein_H = [ {
    'source' : source_protein_H,
    'destination' : destination,
    'percentage' : 0.75,
    'destination_wells' : range((head - 1) * 2 + 2, 97, 8),
    'head' : 2**((head - 1)*2 + 1)
} for head in range(1,4) for destination in destination_plate_list]

task_bosutinib_list = [ {
    'source' : source_bosutinib_list[no - 1],
    'destination' : destination,
    'percentage' : 0.25,
    'destination_wells' : range((no - 1) * 8 + 1, (no - 1) * 8 + 8),
    'heads' : 2**((no - 1) % 6)
} for no in range(1,13) for destination in destination_plate_list]

task_list = task_protein_L + task_protein_H + task_buffer + task_bosutinib_list

# construct list of consumed solutions (reagents) used
volume_needed = dict()

for solution in source_list:
    volume_needed[solution['short']] = 0.0
    
for (task_index, task) in enumerate(task_list):
    source = task['source']
    destination = task['destination']
    volume_needed[source['short']] += task['percentage'] * len(task['destination_wells']) * destination['total_volume']

# Report total volumes needed.
for (solution_index, solution) in enumerate(source_list):
    print "%(name)s:         %(volume)8.3f uL" % { 'name' : solution['name'], 'volume' : volume_needed[solution['short']]}
    
# construct list of consumed solutions (reagents) used
volume_consumed = dict()
for (solution_index, solution) in enumerate(task_list):
    volume_consumed[solution['name']] = 0.0
    
# Maximum possible aspiration volume per head
maximum_dispense_level = 900.0
maximum_head_number = 3

# Fast pipetting
do_fast_pipetting = True

# Number of Aspirations and Dispensings
aspirations = 0
dispenses = 0

# Build worklist.
worklist = ""

loaded_volume = [0.0 in range(1,maximum_head_number + 2)]

for (task_index, task) in enumerate(task_list):
    source = task['source']
    destination = task['destination']
    volume += task['percentage'] * destination['total_volume']
    head = task['head']
    
    for (destination_well_index, destination_well) in enumerate(solution['destination_wells']):      
        if do_fast_pipetting:
            if loaded_volume[head] < volume:
                # aspirate as much as possible
                loaded_volume[head] = 0.0
                worklist += washtips()
        
                possible_volume = (min(maximum_dispense_level, volume_needed[source['short']]) // volume) * volume
                worklist += aspirate(solution['label'], solution['racktype'], solution['well'], possible_volume, dispense_head)
                volume_needed[source['short']] -= possible_volume
                loaded_volume[head] += possible_volume                
    
            if destination['dimensions']==384:
                destination_well = (destination_well - 1) % 8 + ((destination_well - 1) // 8) * 16 + 1

            if not do_fast_pipetting:
                loaded_volume += volume
                worklist += aspirate(source['label'], source['racktype'], source['well'], volume, head)   

            worklist += dispense(destination['label'], destination['racktype'], destination_well, volume, dispense_head)
            loaded_volume[head] -= volume
            volume_consumed[source['short']] += volume            

            if not do_fast_pipetting:
                loaded_volume[head] = 0.0
                worklist += washtips()
    



for (solution_index, solution) in enumerate(task_list):
    for (destination_index, destination) in enumerate(destination_plate_list):    
        volume = destination['total_volume'] * solution['percentage']                
        
        head_list = solution['heads'];
        for (destination_well_index, destination_well_list) in enumerate(solution['destination_wells']):            
            dispense_head =(int)(head_list[destination_well_index]);
            remaining_volume_to_be_aspirated = volume * len(destination_well_list)
            loaded_volume = 0.0
            for destination_well in destination_well_list:
                if do_fast_pipetting:
                    if loaded_volume < volume:
                        # aspirate as much as possible
                        loaded_volume = 0.0
                        worklist += washtips()
                    
                        possible_volume = (min(maximum_dispense_level, remaining_volume_to_be_aspirated) // volume) * volume
                        worklist += aspirate(solution['label'], solution['racktype'], solution['well'], possible_volume, dispense_head)
                        remaining_volume_to_be_aspirated -= possible_volume
                        loaded_volume += possible_volume                
                
                if destination['dimensions']==384:
                    destination_well = (destination_well - 1) % 8 + ((destination_well - 1) // 8) * 16 + 1
            
                if not do_fast_pipetting:
                    loaded_volume += volume
                    worklist += aspirate(solution['label'], solution['racktype'], solution['well'], volume * 1, dispense_head)   
                
                worklist += dispense(destination['label'], destination['racktype'], destination_well, volume, dispense_head)
                loaded_volume -= volume
                volume_consumed[solution['name']] += volume            
            
                if not do_fast_pipetting:
                    loaded_volume = 0.0
                    worklist += washtips()

# Write worklist.
worklist_filename = 'plate_types-worklist.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(worklist)
outfile.close()

# Report total volumes.
for (solution_index, solution) in enumerate(pipetting_list):
    print "%(name)s:         %(volume)8.3f uL" % { 'name' : solution['name'], 'volume' : volume_consumed[solution['name']]}
    
print "Aspirations:  %(number)4d" % { 'number' : aspirations}
print "Dispenses:    %(number)4d" % { 'number' : dispenses}
