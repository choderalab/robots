#!/usr/bin/env python

# March 28, 2014 Jan-Hendrik Prinz and Sonya Hanson play with robot.
# Set up triplicates of Src-Bosutinib binding assay in 5 different plate types.
# Updated with full plate types. March 31, 2014.


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

# Source Definitions

source_protein_L = {
    'name' : 'Protein Low Concentration',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 1,
    'percentage' : 0.75,
    'destination_wells' : range(1, 96, 8) + range(3, 96, 8) + range(5, 96, 8)
}

source_protein_H = {
    'name' : 'Protein High Concentration',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 2,
    'percentage' : 0.75,
    'destination_wells' : range(2, 96, 8) + range(4, 96, 8) + range(6, 96, 8)
}

source_buffer = {
    'name' : 'Buffer',
    'label' : 'Source',
    'racktype' : '5x3 Vial Holder',
    'well' : 3,
    'percentage' : 0.75,
    'destination_wells' : range(7, 96, 8)
}

source_bosutinib_list = [
    {
        'name' : 'Bosutinib #' + str( no ),
        'label' : 'Bosutinib',
        'racktype' : '96 well DeepWell 4ti-0136',
        'well' : (no - 1) * 8 + 1,
        'percentage' : 0.25,
        'destination_wells' : range((no - 1) * 8 + 1, (no - 1) * 8 + 8)
    } for no in range(1,13)
]

pipetting_list = [ source_protein_L, source_protein_H, source_buffer ] + source_bosutinib_list
    
destination_plate_list = [ destination_plate_1, destination_plate_2, destination_plate_3, destination_plate_4, destination_plate_5]

# construct list of solutions (reagents) used
volume_consumed = dict()
for (solution_index, solution) in enumerate(pipetting_list):
    volume_consumed[solution['name']] = 0.0
    
# Maximum possible aspiration volume
maximum_dispense_level = 900.0

# Fast pipetting
do_fast_pipetting = True

# Number of Aspirations and Dispensings
aspirations = 0
dispenses = 0

# Build worklist.
worklist = ""

for (destination_index, destination) in enumerate(destination_plate_list):    
    # Pipette stuff
    
    for (solution_index, solution) in enumerate(pipetting_list):
        volume = destination['total_volume'] * solution['percentage']                
        remaining_volume_to_be_aspirated = volume * len(solution['destination_wells'])
        loaded_volume = 0.0
        
        for destination_well in solution['destination_wells']:
            if do_fast_pipetting:
                if loaded_volume < volume:
                    # aspirate as much as possible
                    loaded_volume = 0.0
                    worklist += washtips()
                    
                    possible_volume = (min(maximum_dispense_level, remaining_volume_to_be_aspirated) // volume) * volume
                    worklist += aspirate(solution['label'], solution['racktype'], solution['well'], possible_volume, 1)
                    remaining_volume_to_be_aspirated -= possible_volume
                    loaded_volume += possible_volume                
                
            if destination['dimensions']==384:
                destination_well = (destination_well - 1) % 8 + ((destination_well - 1) // 8) * 16 + 1
            
            if not do_fast_pipetting:
                loaded_volume += volume
                worklist += aspirate(solution['label'], solution['racktype'], solution['well'], volume * 1, 1)   
                
            worklist += dispense(destination['label'], destination['racktype'], destination_well, volume, 1)
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
