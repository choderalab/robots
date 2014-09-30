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

def washtips(scheme = 1):
    scheme = int(scheme)
    if scheme > 4 or scheme <1:
        # there are only 4 different wash schemes that can be set in the worklist command in evo
        print "ERROR: Wash scheme is not allowed"
    
    return 'W%d;\r\n' % scheme # queue wash tips

def flushliquids():
    return 'F;\r\n' # flush liquids without washing

def breakexecution():
    return 'B;\r\n' # break execution and run all queued commands before continuing

def setDiTi(index):
    return 'S;%d;\r\n' % index # set used Dispensiple Tips Index to be used
    
def decontaminationwash():
    return 'WD;\r\n' # perform a decontamination wash
    
def comment(s):
    return 'C;%s;\r\n' % s # adds a comment that is ignored by EVOware

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

def _to_expression(s):
    
    s = s.strip()
    p = re.compile('[p|n|u|m]?[M|l|%]$')
    
    unit = p.search(s).group()
        
    expr = s[0:-len(unit)]
                
    return expr, unit
    
def _interprete_rangestring(s):
    
    parts = []
    
    for i in range(1,17):
        s = s.replace(chr(64 + i), str(i))

    leftparts = str.split(s, ',')
    for lpart in leftparts:
        if '-' in lpart:
            # range
            split = str.split(lpart, '-')
            parts.extend( range(int(split[0]), int(split[1]) + 1) )
        else:
            if len(lpart) > 0:
                parts.extend( [ int(lpart)] )
        
    return parts
    
def _headToNumber(h):
    return 2**(h - 1)
    
def _interpret_head(s):
    if type(s) is int:
        return s
        
    if type(s) is str:
        return ord(s) - 64
        
    return 0
    
def _heads_to_list(i):
    l = []
    for p in range(0,8):
        if (2**p) & i > 0:
            l.append(p+1)
    return l
    
def _interprete_heads(s):

    ll = []

    if type(s) is str:
        ll = _interprete_rangestring(s)
    
    if type(s) is list:
        
        ll = [_interpret_head(p) for p in s]
        
    return sum([_headToNumber(p) for p in ll])


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
        
    def con(self, mult = ''):
        return (self.MULTIPLICATIONS[self.mult] / self.MULTIPLICATIONS[mult]) * self.value
        
    def logrange(self,other,steps,unit):
        v1 = self.con()
        v2 = other.con()
        
        result = []
        
        if self.type == other.type:    
            result = (np.exp(np.array(range(0,steps)) / float(steps - 1) * (np.log(v2/v1))) * v1 / self.MULTIPLICATIONS[unit]).tolist()
        
        return [ str(n) + unit + self.UNITS[self.unit] for n in result ]
        
        
    @staticmethod
    def amount_from_text(s):
        expr, unit_s = _to_expression(s)
        value = float(expr)

        unit = 'relative'
        
        mult = ''
        
        for c in unit_s:
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
        return [ self.contents[n].con('') if n in self.contents else 0.0 for n in names ]
        
    def to_source(self, well, volume):
        return Source(self, well, volume)

#  The Plate contains the information necessary to bind to the EvoSoftware and refer to the objects on the deck of the robot.
class Plate:
    'A plate is a movable location that can contain wells'

    ALLOWED_RACK_TYPES = ['Corning 3651', '96 Well Microplate', 'Corning 3679', '384 Well Plate', '384 Well Plate', '5x3 Vial Holder' ]    
    REQUIREDMEMBERS = ['type', 'label', 'dimensions']
    
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
            
        # create set of wells for the plate
        self.wells = {}
        self.wells = { PositionToName(el) : Well(position=el, plate=self) for el in allWells(self.dimensions) }
                
    def well(self, s = ":", shift = [0, 0]):
        return WellSet( self.wells.values()).filter(s, shift)
        
    def replaceWell(self, well, pos=None):
        if pos is None:
            pos = well.position;
            
        pos = _interprete_well(pos)
            
        well.plate = self
        well.position = pos
        self.wells[PositionToName(pos)] = well
        
    def copy_from_plate(self, other):
        for pos in self.wells:
            self.wells[pos].set_from(other.wells[pos])
        
    def __hash__(self):
        return hash(self.label)
        
    def __eq__(self, other):
        # Two wells are considered the same, if the plate is the same and the position
        if isinstance(other, self.__class__):
            return (self.label == other.label)
        else:
            return False
            
    def targets(self):
        return WellSet( [ p for p in self.wells.values() if not p.is_source and p.vol() > 0.0 ]).sort()


# Defines a location on a plate with a specific filling volume and a mixture. Some wells are sources and some are destinations in the pipetting process.
# The necessary pipetting jobs are to be computed by the program including (almost) optimal use of the dispense heads available.

class Well:
    'A well is a liquid holding site on a plate'   
    def __init__(self, *initial_data, **kwargs):
        
        self.is_source = False
        
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])        
            
        if not hasattr(self, 'position'):
            self.position = [1,1]
            
        self.position = _interprete_well(self.position)
        
        if hasattr(self, 'plate'):
            self.plate.replaceWell(self)
            
    def set(self, *initial_data, **kwargs):

        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])        
                        
        if hasattr(self, 'plate'):
            self.plate.replaceWell(self)    

    def set_plate(self, plate):
        self.plate = plate
        
    def wellname(self):
        return PositionToName(self.position)
        
    def wellID(self):
        return PositionToWell(self.plate.dimensions, self.position)
    
    def setMixture(self, mix):
        self.mixture = mix
        
    def source(self, volume = None):
        self.is_source = True;
        if volume is not None:
            self.volume = volume
            
    def target(self, volume = None):
        self.is_source = False;
        if volume is not None:
            self.volume = volume
    
    def vol(self):
        if hasattr(self, 'volume'):
            return Concentration(self.volume).con()
        else:
            return 0.0
            
    def set_from(self, other):
        if hasattr(other, 'position'):
            self.position = other.position
        
        if hasattr(other, 'mixture'):
            self.mixture = other.mixture
            
        if hasattr(other, 'is_source'):
            self.is_source = other.is_source
            
        if hasattr(other, 'volume'):
            self.volume = other.volume
            
        if hasattr(other, 'plate'):
            self.plate = other.plate
            
    def copy(self):
        new_well = Well({})
        new_well.set_from(self)
        
        return new_well
                
    def __hash__(self):
        return hash(self.position[0]) ^ hash(self.position[1]) ^ hash(self.plate)
        
    def __eq__(self, other):
        # Two wells are considered the same, if the plate is the same and the position
        if isinstance(other, self.__class__):
            return (self.position == other.position and self.plate == other.plate)
        else:
            return False
            
    def compute_mixing(self, sources):
        # make list of all parts
        inNames = set([ b for c in sources for b in c.mixture.all_names() ])
        outNames = set([ b for b in self.mixture.all_names() ])
            
        missing = outNames - inNames

        if len(missing) > 0:
            # there are some part missing to produce the output
            for c in missing:
                print "Missing : ", c
    
        order = list(outNames)

        mat = np.transpose(np.array([source.mixture.concentrations(order) for source in sources]))
        vec = np.array(self.mixture.concentrations(order))
        
        percentage = np.linalg.lstsq(mat,vec)
            
        return percentage[0].tolist()
        
class Source(Well):
    def __init__(self, *initial_data, **kwargs):
        Well.__init__(self,*initial_data, **kwargs)
        self.is_source = True;
        
class WellSet(list):
    'A WellSet is a set of wells on one or more plates'
    
    def position_list(self):
        return [ el.position for el in self ]
        
    def well_list(self):
        return [ PositionToWell(el.plate.dimensions, el.position) for el in self ]
    
    def filter(self, s = ":", shift = [0, 0]):
        parts = str.split(s.replace(' ', ''), ';')
                
        welllist = []
        
        for part in parts:
            rows = []
            cols = []
            if ':' in part:
                #extended list
                split = str.split(part, ':')
                left = split[0]
                right = split[1]
                
                for i in range(1,17):
                    left = left.replace(chr(64 + i), str(i))
                
                leftparts = str.split(left, ',')
                for lpart in leftparts:
                    if '-' in lpart:
                        # range
                        split = str.split(lpart, '-')
                        rows.extend( range(int(split[0]), int(split[1]) + 1) )
                    else:
                        if len(lpart) > 0:
                            rows.extend( [ int(lpart)] )
                        
                rightparts = str.split(right, ',')
                for rpart in rightparts:
                    if '-' in rpart:
                        # range
                        split = str.split(rpart, '-')
                        cols.extend( range(int(split[0]), int(split[1]) + 1) )
                    else:
                        if len(rpart) > 0:
                            cols.extend( [ int(rpart)] )
            else:
                if len(part) > 1:
                    rows = [ ord(part[0]) - 64 ]
                    cols = [ int(part[1:]) ]
                                    
            if len(cols) == 0:
                cols = range(1, 25)

            if len(rows) == 0:
                rows = range(1, 17)
                
            welllist.extend( [ [i,j] for i in rows for j in cols ] )
                                                
        wellnamelist = [ PositionToName(p) for p in welllist ]
        
        return WellSet( [ p for p in self if PositionToName(p.position) in wellnamelist ] )

    def sort(self):
        return sorted(self, key=lambda x: x.position[1]*100 + x.position[0])
                
    def mixture(self, mixtures):
        'liquid sets the mixture types for all wells'
        return WellSet([ el.setMixture(mixtures[el.wellname()]) for el in self ])
        
    def plate(self, plate):
        return WellSet([ el.set_plate(plate) for el in self ])
    
def replace_value(s, key, val, val_min, val_max):
    
    if val_min < val_max:
        val_percent = 1.0 * (val - val_min) / (val_max - val_min)
    else:
        val_percent = 1.0
    
    s = s.replace( '{' + key + '}', str(val))
    s = s.replace( '{%(' + key + ')}', str(val_percent))
    
    return s

def apply_rule(plate, rule):
    well_list = []
    
    plate_okay = True
    
    if 'target' in rule:
        if re.search(rule['target'], plate.label):
            plate_okay = True
        else:
            plate_okay = False
        
    if plate_okay:            
        if 'wells' in rule:
            well_list = plate.well(rule['wells'])
            cols = []
            rows = []
    
            for well in well_list:
                cols.append(well.position[1])
                rows.append(well.position[0])
        
            row_min = min(rows)
            row_max = max(rows)
    
            col_min = min(cols)
            col_max = max(cols)
    
        if 'mixture' in rule:
            mixture = rule['mixture']
            cmd = rule['cmd']
        
            for well in well_list:
                col = well.position[1]
                row = well.position[0]
        
                if cmd == 'set':
                    well.mixture = Mixture({})
                
                for (substance, conc) in rule['mixture'].iteritems():
            
                    substance = replace_value(substance, 'row', row, row_min, row_max)
                    substance = replace_value(substance, 'col', col, col_min, col_max)
            
                    concentration, unit = _to_expression(conc)

                    concentration = replace_value(concentration, 'row', row, row_min, row_max)
                    concentration = replace_value(concentration, 'col', col, col_min, col_max)
            
                    concentration = str(eval(concentration))
            
                    if not hasattr(well, 'mixture'):
                        well.mixture = Mixture({})
            
                    well.mixture.contents[substance] = Concentration(str(concentration) + unit)
                
        if 'volume' in rule:
            for well in well_list:
                col = well.position[1]
                row = well.position[0]
            
                volume, unit = _to_expression(rule['volume'])
            
                volume = replace_value(volume, 'row', row, row_min, row_max)
                volume = replace_value(volume, 'col', col, col_min, col_max)
            
                volume = str(eval(volume))
            
                well.volume = volume + unit
            
class TaskRule(object):
    def __init__(self, *initial_data, **kwargs):
        
        self.is_source = False
        
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])


source_plate = Plate({
    'name' : 'Protein and Buffer',
    'label' : 'Source',
    'dimensions' : [8,12],
    'type' : '5x3 Vial Holder',
    'maximum_volume' : 100,
})

source_protein_L = Source({
    'name' : 'Protein Low Concentration',
    'short' : 'Protein_Low',
    'plate' : source_plate,
    'mixture' : Mixture({ 
        'Protein_L' : '100%'
    }),
    'volume' : '10ml',
    'position' : 'A1'
    }
)

source_protein_H = Source({
    'name' : 'Protein High Concentration',
    'short' : 'Protein_High',
    'plate' : source_plate,
    'mixture' : Mixture({ 
        'Protein_H' : '100%'
    }),
    'volume' : '10ml',
    'position' : 'B1'
    }
)

source_buffer = Source({
    'name' : 'Buffer Solution',
    'short' : 'Buffer',
    'plate' : source_plate,
    'mixture' : Mixture({ 
        'Buffer' : '100%'
    }),
    'volume' : '10ml',
    'position' : 'C1'
    }
)

source_bosutinib_list = [
    Source({
        'name' : 'Bosutinib #' + str(no),
        'short' : 'Bosutinib' + str(no),
        'plate' : source_plate,
        'mixture' : Mixture({ 
            'Bosutinib#' + str(no) : '100%'
        }),
        'volume' : '10ml',
        'position' : 'C1'
        }
    )
    for no in range(1,13)
]

source_list = [source_protein_L, source_protein_H, source_buffer ] + source_bosutinib_list

###############################################################################        
##  PLATE DEFINITIONS
###############################################################################
    
# Destination Plate Definitions

destination_plate_1 = Plate({
    'label' : 'Corning3651',
    'type' : 'Corning 3651',
    'dimensions' : [8, 12],
    'maximum_volume' : '200ul'
})

destination_plate_2 = Plate({
    'label' : '96well-UVStar',
    'type' : '96 Well Microplate',
    'dimensions' : [8, 12],
    'maximum_volume' : '200ul'
})

destination_plate_3 = Plate({
    'label' : 'Corning3679',
    'type' : 'Corning 3679',
    'dimensions' : [8, 12],
    'maximum_volume' : '100ul'
})

destination_plate_4 = Plate({
    'label' : '384well',
    'type' : '384 Well Plate',
    'dimensions' : [16, 24],
    'maximum_volume' : '50ul'
})

destination_plate_5 = Plate({
    'label' : '384well2',
    'type' : '384 Well Plate',
    'dimensions' : [16, 24],
    'maximum_volume' : '50ul'
})

destination_plate_6 = Plate({
    'label' : '384well3',
    'type' : '384 Well Plate',
    'dimensions' : [16, 24],
    'maximum_volume' : '50ul'
})

destination_plate_list = [ destination_plate_1, destination_plate_2, destination_plate_3, destination_plate_4, destination_plate_5, destination_plate_6]

well_rules = [
    { 'cmd' : 'set', 'wells': 'A,C,E:1-12', 'mixture' : { 'Protein_H' : '75%'} },
    { 'cmd' : 'set', 'wells': 'B,D,F:1-12', 'mixture' : { 'Protein_L' : '75%'} },
    { 'cmd' : 'set', 'wells': 'G:1-12', 'mixture' : { 'Buffer' : '75%'} },
    { 'cmd' : 'add', 'wells': 'A-G:1-12', 'mixture' : { 'Bosutinib#{col}' : '25%'} },
    { 'target' : 'Corning3651', 'wells' : 'A-G:1-12', 'volume' : '75ul'},
    { 'target' : '96well-UVStar', 'wells' : 'A-G:1-12', 'volume' : '75ul'},
    { 'target' : 'Corning3679', 'wells' : 'A-G:1-12', 'volume' : '50ul'},
    { 'target' : '384well(.*)', 'wells' : 'A-G:1-12', 'volume' : '20ul'}
#    { 'cmd' : 'add', 'wells': 'A-G:1-11', 'mixture' : { 'Compound #1' : '100 ** {%(col)} nM'} }
]

well_rules = [
    { 'cmd' : 'set', 'wells': 'A,C,E:1-12', 'mixture' : { 'Protein_H' : '100%'} },
    { 'cmd' : 'set', 'wells': 'B,D,F:1-12', 'mixture' : { 'Protein_L' : '100%'} },
    { 'cmd' : 'set', 'wells': 'G:1-12', 'mixture' : { 'Buffer' : '100%'} },
    { 'target' : 'Corning3651', 'wells' : 'A-G:1-12', 'volume' : '75 ul'},
    { 'target' : '96well-UVStar', 'wells' : 'A-G:1-12', 'volume' : '75ul'},
    { 'target' : 'Corning3679', 'wells' : 'A-G:1-12', 'volume' : '50ul'},
    { 'target' : '384well(.*)', 'wells' : 'A-G:1-12', 'volume' : '20ul'}
#    { 'cmd' : 'add', 'wells': 'A-G:1-11', 'mixture' : { 'Compound #1' : '100 ** {%(col)} nM'} }
]

rules = [ 
    TaskRule({ 'source' : '', 'head' : '1-7', 'assignment' : 'row' }),
    TaskRule({ 'source' : 'Bosutinib(.*?)', 'head' : '1-6', 'assignment' : 'free' })
]

for plate in destination_plate_list:
    for rule in well_rules:
        apply_rule(plate, rule)
        
# GENERATE TASKS

tasks = [
    {
        'source' : source_list[source_index],
        'target' : well,
        'volume' : Concentration(str(well.vol() * mix) + 'l')
    }
    for plate in destination_plate_list
    for well in plate.targets()
    for (source_index, mix) in enumerate(well.compute_mixing(source_list))
    if mix > 0.0
]

tasks = [
    task
    for source in source_list
    for plate in destination_plate_list
    for task in sorted(tasks, key=lambda x: x['target'].position[0]*100 + x['target'].position[1])
    if task['target'].plate.label == plate.label and task['source'].short == source.short
]

head_substance = dict()

for rule in rules:
    free_heads = _heads_to_list(_interprete_heads(rule.head))
    head_choice = 0;
    for task in tasks:
    
        if re.match(rule.source, task['source'].short):
            pos = task['target'].position
            target_row = pos[0]
            target_col = pos[1]
        
            t = rule.assignment
            if t == 'row':
                head = target_row
            if t == 'free':
                if task['source'].short in head_substance:
                    head = head_substance[task['source'].short]
                else:
                    head = free_heads[head_choice]
                    head_substance[task['source'].short] = head
                    head_choice += 1
                    if head_choice == len(free_heads):
                        head_choice = 0
                    
            task['head'] = head
                    

# construct list of consumed solutions (reagents) used
volume_needed = dict()
volume_dispenses = dict()
volume_consumed = dict()

for solution in source_list:
    volume_needed[solution.short] = 0.0
    volume_consumed[solution.short] = 0.0
        

# Maximum possible aspiration volume per head
maximum_dispense_level = 900.0
maximum_head_number = 8

# Fast pipetting
do_fast_pipetting = True

# Number of Aspirations and Dispenses
aspirations = 0
dispenses = 0

# Build worklist.
worklist = ""

# Running state of the head
dispense_volumes = [[] for p in range(1, 10)]
loaded_volume = [0.0 for p in range(1, 10)]
loaded_source = ['' for p in range(1, 10)]

for task in tasks:
    source = task['source']
    destination = task['target']
    volume = task['volume'].con('u')
    head = task['head']
    
    if loaded_source[head] == '':
        loaded_source[head] = source.short
    
    volume_needed[source.short] += volume
    loaded_volume[head] += volume
    if (loaded_volume[head] > maximum_dispense_level) or (source.short != loaded_source[head]):
        loaded_source[head] = source.short
        # aspirate as much as possible
        dispense_volumes[head].append( loaded_volume[head] - volume )
        loaded_volume[head] = volume
                                                            
for index in range(1,9):
    dispense_volumes[index].append( loaded_volume[index] )
    loaded_volume[index] = 0.0
    

# dispense
for index in range(1,9):
    print index," aspirates : ", dispense_volumes[index]
    
dispense_index = [0 for p in range(1, 257)]

first_aspirate = True

for task in tasks:
    source = task['source']
    destination = task['target']
    volume = task['volume'].con('u')
    head = task['head']

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
            
            volume_needed[source.short] -= possible_volume
            loaded_volume[head] += possible_volume                
                            
            worklist += aspirate(source.plate.label, source.plate.type, source.wellID(), possible_volume, head)

        worklist += dispense(destination.plate.label, destination.plate.type, destination.wellID(), volume, head)
        loaded_volume[head] -= volume
        volume_consumed[source.short] += volume

worklist_filename = 'plate_types-worklist-protein_new-final.gwl'
outfile = open(worklist_filename, 'w')
outfile.write(worklist)
outfile.close()

# Report total volumes needed.
for (solution_index, solution) in enumerate(source_list):
    print "%(name)s:         %(volume)8.3f uL" % { 'name' : solution.short, 'volume' : volume_needed[solution.short]}


# Report total volumes.
for (solution_index, solution) in enumerate(source_list):
    print "%(name)s:         %(volume)8.3f uL" % { 'name' : solution.short, 'volume' : volume_consumed[solution.short]}

for index in range(1,9):
    print "%(head)s:         %(volume)8.3f uL" % { 'head' : index, 'volume' : loaded_volume[index]}
    

print "Aspirations:  %(number)4d" % { 'number' : aspirations}
print "Dispenses:    %(number)4d" % { 'number' : dispenses}