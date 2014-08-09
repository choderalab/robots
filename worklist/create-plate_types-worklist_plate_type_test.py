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
