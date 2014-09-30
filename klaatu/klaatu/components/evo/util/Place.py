'''
Created on 14.04.2014

@author: jan-hendrikprinz
'''

class PlateLocation(object):
    '''
    classdocs
    '''

    def __init__(self, params):
        '''
        Constructor
        '''
        if type(params) is list:
            self._p = params
            
        if type(params) is str:
            self._p = self._n2p(params)
        
    def from_well_id(self, well, size):
        self._p = [(well - 1) % size[0] + 1, (well - 1) // size[0] + 1]
    
    def well_id(self, size):
        return (self._p[1] - 1) * size[0] + self._p[0]    
    
    @staticmethod
    def _p2n(pos):
        return chr(64 + pos[0]) + str(pos[1])

    @staticmethod    
    def _n2p(s):
        return [ord(s[0]) - 64, int(s[1:])]
    

class PlateLocationList(list):
    
    def __init__(self, s = ':', shift = [0, 0], plate = [8,12]):
        self.plate = plate
        self.extend(self._parse(s, shift))
            
    
    def position_list(self):
        return [ el._p for el in self ]
                                                      
    def _parse(self, s = ':', shift = [0, 0]):
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
                cols = range(1, self.plate[1] + 1)

            if len(rows) == 0:
                rows = range(1, self.plate[0] + 1)
                
            welllist.extend( [ [i,j] for i in rows for j in cols ] )
            
        return welllist
    
    def __add__(self, other):        
        for psr in other:
            if not psr in self:
                self.append(psr) 
                
        return self
        
    __or__ = __add__
    
    def __and__(self, other):
        removes = [psr for psr in self if not psr in other]
        [ self.remove(psr) for psr in removes] 
                
        return self
    
    def __sub__(self, other):
        [ self.remove(psr) for psr in other if psr in self] 
                
        return self

    def sort(self):
        return sorted(self, key=lambda x: x._p[1]*100 + x._p[0])
    
    
pll = PlateLocationList('A-G:1-9')
pll2 = PlateLocationList('A,C,E,G:1-9')

PLL = PlateLocationList                