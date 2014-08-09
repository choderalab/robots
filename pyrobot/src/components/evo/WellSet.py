'''
Created on 14.04.2014

@author: jan-hendrikprinz
'''

import util.Parser as ps

class WellSet(list):
    'A WellSet is a set of wells on one or more plates'
    
    def position_list(self):
        return [ el.position for el in self ]
        
    def well_list(self):
        return [ ps.PositionToWell(el.plate.dimensions, el.position) for el in self ]
    
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
                                                
        wellnamelist = [ ps.PositionToName(psr) for psr in welllist ]
        
        return WellSet( [ psr for psr in self if ps.PositionToName(psr.position) in wellnamelist ] )

    def sort(self):
        return sorted(self, key=lambda x: x.position[1]*100 + x.position[0])
                
    def mixture(self, mixtures):
        'liquid sets the mixture types for all wells'
        return WellSet([ el.setMixture(mixtures[el.wellname()]) for el in self ])
        
    def plate(self, plate):
        return WellSet([ el.set_plate(plate) for el in self ])