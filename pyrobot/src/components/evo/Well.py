import util.Parser as ps
import numpy as np

import util.Units as u

size96 = [8, 12]
size384 = [16, 24]

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
            
        self.position = ps._interprete_well(self.position)
        
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
        return ps.PositionToName(self.position)
        
    def wellID(self):
        return ps.PositionToWell(self.plate.dimensions, self.position)
    
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
            return u.V(self.volume).val()
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