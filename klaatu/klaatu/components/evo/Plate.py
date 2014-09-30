"""
Created on 14.04.2014

@author: jan-hendrikprinz
"""

import re

from klaatu.components.evo.Well import Well
from klaatu.components.evo.WellSet import WellSet
from klaatu.components.evo.Mixture import Mixture
from klaatu.util.evo.Units import C
import klaatu.util.evo.WellParser as ps

#  The Plate contains the information necessary to bind to the EvoSoftware and refer to the objects on the deck of the robot.
class Plate:
    """A plate is a movable location that can contain wells"""

    ALLOWED_RACK_TYPES = ['Corning 3651', '96 Well Microplate', 'Corning 3679', '384 Well Plate', '384 Well Plate', '5x3 Vial Holder' ]    
    REQUIREDMEMBERS = ['racktype', 'label', 'dimensions']
    
    PLATE_TEMPLATES = [
        {
            'dimensions' : [3,5],
            'racktype' : '5x3 Vial Holder',
            'maximum_volume' :' 10000ul'
        },
        {
            'racktype' : 'Corning 3651',
            'dimensions' : [8, 12],
            'maximum_volume' : '200ul'
        },
        {
            'racktype' : '96 Well Microplate',
            'dimensions' : [8, 12],
            'maximum_volume' : '200ul'
        },
        {
            'racktype' : 'Corning 3679',
            'dimensions' : [8, 12],
            'maximum_volume' : '100ul'
        },
        {
            'racktype' : '384 Well Plate',
            'dimensions' : [16, 24],
            'maximum_volume' : '50ul'
        }
    ]
    
    def __init__(self, *initial_data, **kwargs):
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
                        
#        for key in self.REQUIREDMEMBERS:
#            if not hasattr(self, key):
#                print 'ERROR: Missing information for plate: ' + key
                
#        if self.racktype not in self.ALLOWED_RACK_TYPES:
#            print 'ERROR: plate racktype not allowed/registered: ' + self.racktype
        
        self.template()
            
        # create set of wells for the plate
        
        self.wells = {}
        self.wells = { ps.PositionToName(el) : Well(position=el, plate=self) for el in ps.allWells(self.dimensions) }
        
                
    def well(self, s = ":", shift = [0, 0]):
        return WellSet( self.wells.values()).filter(s, shift)
        
    def replaceWell(self, well, pos=None):
        if pos is None:
            pos = well._p

        pos = ps._interprete_well(pos)
            
        well.plate = self
        well._p = pos
        self.wells[ps.PositionToName(pos)] = well
        
    def copy_from_plate(self, other):
        for pos in self.wells:
            self.wells[pos].set_from(other.wells[pos])
        
    def __hash__(self):
        return hash(self.label)
        
    def __eq__(self, other):
        # Two wells are considered the same, if the plate is the same and the _p
        if isinstance(other, self.__class__):
            return self.label == other.label
        else:
            return False
            
    def targets(self):
        return WellSet( [ psr for psr in self.wells.values() if not psr.is_source and psr.vol() > 0.0 ]).sort()
    
    def template(self, racktype = None):
        if racktype is None:
            racktype = self.racktype
        
        if racktype != '':
            temp = [ psr for psr in self.PLATE_TEMPLATES if psr['racktype'] == racktype][0]
            self.dimensions = temp['dimensions']
            self.maximum_volume = temp['maximum_volume']
            self.racktype = temp['racktype']
        
    def apply_rule(self, rule_list):    
        
        if type(rule_list) is not list:
            rule_list = [ rule_list ]
            
        for rule in rule_list:            
            well_list = []
            
            plate_okay = True
            
            if 'target' in rule:
                if re.search(rule['target'], self.label):
                    plate_okay = True
                else:
                    plate_okay = False
                
            if plate_okay:            
                if 'wells' in rule:
                    well_list = self.well(rule['wells'])
                    cols = []
                    rows = []
            
                    for well in well_list:
                        cols.append(well._p[1])
                        rows.append(well._p[0])
                
                    row_min = min(rows)
                    row_max = max(rows)
            
                    col_min = min(cols)
                    col_max = max(cols)
            
                if 'mixture' in rule:            
                    for well in well_list:
                        col = well._p[1]
                        row = well._p[0]
                
                        for (substance, conc) in rule['mixture'].iteritems():
                    
                            substance = ps.replace_value(substance, 'row', row, row_min, row_max)
                            substance = ps.replace_value(substance, 'col', col, col_min, col_max)
                    
                            concentration, unit = ps._to_expression(conc)
        
                            concentration = ps.replace_value(concentration, 'row', row, row_min, row_max)
                            concentration = ps.replace_value(concentration, 'col', col, col_min, col_max)
                    
                            concentration = str(eval(concentration))
                    
                            if not hasattr(well, 'mixture'):
                                well.mixture = Mixture({})
                    
                            well.mixture.contents[substance] = C(str(concentration) + unit)
                        
                if 'volume' in rule:
                    for well in well_list:
                        col = well._p[1]
                        row = well._p[0]
                    
                        volume, unit = ps._to_expression(rule['volume'])
                                    
                        volume = ps.replace_value(volume, 'row', row, row_min, row_max)
                        volume = ps.replace_value(volume, 'col', col, col_min, col_max)
                    
                        volume = str(eval(volume))
                    
                        well.volume = volume + unit
