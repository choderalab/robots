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

import re
import numpy as np

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
    return (pos[1] - 1) * h + pos[0]    

def PositionToName(pos):
    return chr(64 + pos[0]) + str(pos[1])

def NameToPosition(str):
    return [ord(str[0]) - 64, int(str[1:])]

def WellToName(size, well):
    return PositionToName( WellToPosition(size,well))

def NameToWell(size, str):
    return PositionToWell(size, NameToPosition(str))

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
        return NameToPosition(el)
    
    
rowA = dict([ ( chr(64 + r), range(r, 97, 8)) for r in range(1,9) ] + [ (r, range(r, 97, 8)) for r in range(1,9) ])
row = [ range(r, 97, 8) for r in range(1,9) ]
colA = dict([ (r, range((r - 1)*8 + 1, (r - 1)*8 + 9)) for r in range(1,13) ])
col = [ range((r - 1)*8 + 1, (r - 1)*8 + 9) for r in range(1,13) ]
    

###############################################################################        
##  CLASS DEFINITIONS - not used yet
###############################################################################

# This is to decorate strings that contain liquid names to make sure only valid liquid names are used.  
class Concentration:
    MULTIPLICATIONS = {
        '' : 1,
        '%' : 1e-2,
        'm' : 1e-3,
        'u' : 1e-6, 
        'n' : 1e-9, 
        'p' : 1e-12, 
    }
    
    UNITS = {
        'relative' : '',
        'molar' : 'M',
        'volume' : 'l'
    }
    
    def __init__(self, s):
        concentration = self.amount_from_text(s)
        self.unit = concentration['unit']
        self.mult = concentration['mult']
        self.value = concentration['value']
        if self.unit == 'molar':
            self.type = 'compound'
        else:
            self.type = 'liquid'
        
    def __str__(self):
        return str(self.value) + self.mult + self.UNITS[self.unit]
        
    def __repr__(self):
            return str(self.value) + self.mult + self.UNITS[self.unit]
        
    def con(self):
        return self.MULTIPLICATIONS[self.mult] * self.value
        
    def logrange(self,other,steps,unit):
        v1 = self.con()
        v2 = other.con()
        
        result = []
        
        if self.type == other.type:    
            result = (np.exp(np.array(range(0,steps)) / float(steps - 1) * (np.log(v2/v1))) * v1 / self.MULTIPLICATIONS[unit]).tolist()
        
        return [ str(n) + unit + self.UNITS[self.unit] for n in result ]
        
        
    @staticmethod
    def amount_from_text(s):
        p = re.compile('[0-9.]+')
        value = float(p.match(s).group())

        unit = 'relative'
        
        for c in s:
            if c == "M":
                unit = "molar"
            if c == "l":
                unit = "volume"
            if c == "%":
                unit = "relative"
                mult = '%'
            if c == "u":
                mult = 'u'
            if c == "m":
                mult = 'm'
            if c == "n":
                mult = 'n'
            if c == "p":
                mult = 'p'
            
        return { 
            'value' : value, 
            'unit' : unit, 
            'mult' : mult, 
        }

class Substance:
    'A liquid is named fluid that is to be transported from one'    
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
            
        if not hasattr(self, 'concentration'):
            self.concentration = 1.0

class Liquid(Substance):
    def __init__(self, substance):
        
        self.name = substance.items()[0][0]
        
        concentration = _interprete_unit(substance.items()[0][1])
        self.concentration = concentration

class Compound(Substance):
    def __init__(self, substance):
        
        self.name = substance.items()[0][0]

        concentration = _interprete_unit(substance.items()[0][1])
        self.concentration = concentration

class Mixture:
    'A mixture is a description for a combination of one or more liquids with their respective concentrations'
    def __init__(self, content):
        self.contents = {p : Concentration(content[p]) for p in content}
        
    def __str__(self):
        output = ''
        for s in self.contents:
            output += s + ' : ' + str(self.contents[s]) + ", "
            
        return output
        
    def liquids(self):
        return {p : self.contents[p] for p in self.contents if self.contents[p].type == 'liquid'}
        
    def liquid_names(self):
        return self.liquids().keys()
        
    def compounds(self):
        return {p : self.contents[p] for p in self.contents if self.contents[p].type == 'compound'}
        
    def all_names(self):
        return self.contents.keys()
        
    def compound_names(self):
        return self.compounds().keys()
        
    def concentrations(self, names):
        return [ self.contents[n].con() if n in self.contents else 0.0 for n in names ]
        
    def to_source(self, well, volume):
        return Source(self, well, volume)
            

def compute_mixing(sources, output):
    # make list of all parts
    inNames = set([ b for c in sources for b in c.all_names() ])
    outNames = set([ b for b in output.all_names() ])
    
    missing = outNames - inNames

    if len(missing) > 0:
        # there are some part missing to produce the output
        for c in missing:
            print "Missing : ", c
    
    order = list(outNames)

    mat = np.transpose(np.array([source.concentrations(order) for source in sources]))
    vec = np.array(output.concentrations(order))
    
    percentage = np.linalg.lstsq(mat,vec)
    
    return percentage[0].tolist()

class Source(Mixture):
    'A Source is a mixture of liquids and compounds with a well associated where the liquid is found'
    def __init__(self, mixture, well, volume):
        super(ChildB, self).__init__(mixture)
        self.well = well;
        self.volume = volume;
            
    
# source = Source({'Buffer': '100%', 'Bosutinib': '5uM'})


#  The Plate contains the information necessary to bind to the EvoSoftware and refer to the objects on the deck of the robot.
class Plate:
    'A plate is a movable location that can contain wells'

    ALLOWED_RACK_TYPES = ['Corning 3651', '96 Well Microplate', 'Corning 3679', '384 Well Plate', '384 Well Plate' ]    
    REQUIREDMEMBERS = ['type', 'label', 'dimensions']
    
#    def __init__(self, type='', dimensions = size96, name = '', label = '', description = ''):
#        self.type = type
#        self.label = label
#        self.name = name
#        self.description = description
#        self.dimensions = dimensions
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
                        
        for key in self.REQUIREDMEMBERS:
            if not hasattr(self, key):
                print 'ERROR: Missing information for plate: ' + key
                
        if self.type not in self.ALLOWED_RACK_TYPES:
            print 'ERROR: plate type not allowed/registered: ' + self.type
        
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
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])        
            
        if not self.position:
            self.position = [1,1]
            
        self.position = _interprete_well(self.position)

    def set_plate(self, plate):
        self.plate = plate
        
    def wellname(self):
        return PositionToName(self.position)
    
    def setMixture(self, mix):
        self.mixture = mix
                
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
        
    def well_list(self):
        return [ PositionToWell(el.plate.dimensions, el.position) for el in self ]
    
    def filter(self, rows=None, cols=None, wells=[]):
        if rows is None:
            rows = range(1,17)
    
        if cols is None:
            cols = range(1,25)
            
        rows = [ _interprete_row(el) for el in rows ]

        return WellSet([
                el for el in self if ((el.position[0] in rows) and (el.position[1] in cols)) or (el.position in wells) 
            ])
                
    def mixture(self, mixtures):
        'liquid sets the mixture types for all wells'
        return WellSet([ el.setMixture(mixtures[el.wellname()]) for el in self ])
        
    def plate(self, plate):
        return WellSet([ el.set_plate(plate) for el in self ])

l1 = Mixture({ 'Buffer' : '100%'})
l2 = Mixture({ 'DMSO' : '100%'})

c1 = Mixture({ 'Bosutinib' : '10mM', 'DMSO' : '100%'})
c2 = Mixture({ 'Src' : '10mM', 'Buffer' : '100%'})

mm = Mixture({ 'Buffer' : '99%', 'DMSO' : '1%', 'Bosutinib' : '50uM', 'Src' : '1mM'})

pl = Plate(dimensions=[3,5], name='Corning 3651', type='Corning 3679', label='Source')

ws1 = pl.wells()            
ws2 = ws1.filter(cols=range(2,5))

print ws2.position_list()
print ws2.well_list()
print ws2[0].plate.name
print len(ws2.filter(rows=[1]))

dest_plate_1 = Plate({
    'label' : 'Corning3651',
    'type' : 'Corning 3651',
    'total_volume' : 75,
    'dimensions' : [8, 12],
    'maximum_volume' : 100,
    'well_shift' : 0
})

bosutinib_concentrations = Concentration('50uM').logrange(Concentration('100uM'), steps=12, unit='u')
protein_concentrations = Concentration('0.01uM').logrange(Concentration('1mM'), steps=8, unit='u')

wl1 = dest_plate_1.wells()

mixture_list = {
    PositionToName(pos) : Mixture({ 
        'Buffer' : '99%',
        'DMSO' : '1%', 
        'Bosutinib' : bosutinib_concentrations[pos[1] - 1], 
        'Src' : protein_concentrations[pos[0] - 1]
    })
    for pos in wl1.position_list()
}

wl2 = wl1.filter(rows = ['A','C','E'])
wl3 = wl1.filter(rows = ['B','D','F'])

for index, well in enumerate(wl2):
    wl2[index].setMixture(
        Mixture({ 
            'Bosutinib#' + str(well.position[1]) : '25%', 
            'SrcLow' : '75%'
        })
    )

for index, well in enumerate(wl3):
    wl3[index].setMixture(
        Mixture({ 
            'Bosutinib#' + str(well.position[1]) : '25%', 
            'SrcHigh' : '75%'
        })
    )

bosutinibs = [ Mixture({ 'Bosutinib#' + str(col) : '100%'}) for col in range(1,13) ]
src = [ Mixture({ 'SrcLow' : '100%'}).to_source() , Mixture({ 'SrcHigh' : '100%'}) ]

print wl2[0].mixture.all_names()

for w in wl2:
    erg = compute_mixing(src + bosutinibs, w.mixture)[0]
    {
        'source' : source_buffer,
        'destination' : destination,
        'percentage' : 1.00,
        'destination_wells' : range(7, 97, 8),
        'head' : 64
    }
    
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
