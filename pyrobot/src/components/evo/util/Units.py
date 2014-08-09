'''
Created on 14.04.2014

@author: jan-hendrikprinz
'''

import re

class UnitScalar():
    MULTS = {
        '' : 1.0,
        'm' : 1e-3,
        'u' : 1e-6, 
        'n' : 1e-9, 
        'psr' : 1e-12,
        'f' : 1e-15 
    }
    UNITS = [ '' ]
        
    def __init__(self, s):
        self._parse(s)


    def __str__(self):
        return str(self.value / self.MULTS[self.mult]) + ' ' + self.mult + self.unit
        
    def __repr__(self):
        return 'V(\'' + str(self.value) + self.mult + self.unit + '\')'
        
    def val(self, mult = None, unit = None):
        if mult is None:
            mult = self.mult
            
        if unit is None:
            unit = self.unit
            
        return self.value / self.MULTS[mult] / self.UNITS[unit]
    
    def __add__(self, other):
        if type(other) in [float, int]:
            return self.__class__(str((self.value + other) / self.MULTS[self.mult] / self.UNITS[self.unit]) + self.mult + self.unit)
        
        if isinstance(other, UnitScalar):
            if self.__class__ != other.__class__:
                raise ValueError('Incompatible Units')

            mult = self.mult
            if self.MULTS[self.mult] < self.MULTS[other.mult]:
                mult = other.mult
                
            return self.__class__(str((self.value + other.value) / self.MULTS[mult] / self.UNITS[self.unit] ) + mult + self.unit)
    
    def __sub__(self, other):
        if type(other) in [float, int]:
            return self.__class__(str((self.value - other) / self.MULTS[self.mult] / self.UNITS[self.unit]) + self.mult + self.unit)
        
        if isinstance(other, UnitScalar):
            if self.__class__ != other.__class__:
                raise ValueError('Incompatible Units')

            mult = self.mult
            if self.MULTS[self.mult] < self.MULTS[other.mult]:
                mult = other.mult
                
            return self.__class__(str((self.value - other.value) / self.MULTS[mult] / self.UNITS[self.unit] ) + mult + self.unit)
        
    def __mul__(self, other):
        if type(other) in [float, int]:
            return self.__class__(str((self.value * other) / self.MULTS[self.mult] / self.UNITS[self.unit]) + self.mult + self.unit)
        
        if isinstance(other, UnitScalar):
            if not (self.unit in ['%', ''] or other.unit in ['%', '']):
                raise ValueError('Needs multiplication with scalar')

            if self.unit in ['%', '']:
                mult = other.mult
                unit = other.unit
                return other.__class__(str((self.value * other.value) / other.MULTS[mult] / self.UNITS[unit]) + mult + unit)
            else:
                mult = self.mult
                unit = self.unit
                return self.__class__(str((self.value * other.value) / self.MULTS[mult] / self.UNITS[unit]) + mult + unit)
            
                    
    def __div__(self, other):
        if type(other) in [float, int]:
            return self.__class__(str((self.value / other) / self.MULTS[self.mult] / self.UNITS[self.unit]) + self.mult + self.unit)
        
        if isinstance(other, UnitScalar):
            if not (other.unit in ['%', '']):
                raise ValueError('Needs multiplication with scalar')
            else:
                mult = self.mult
                unit = self.unit
                return self.__class__(str((self.value / other.value) / self.MULTS[mult] / self.UNITS[unit]) + mult + unit)
                
    def adjust(self):
        for mult in self.MULTS:
            val = self.value / self.MULTS[mult] / self.UNITS[self.unit]
            if val>=1.0 and val<1000.0:
                self.mult = mult
        
        return self
                
    __radd__ = __add__
    __rmul__ = __mul__

                
    def _parse(self, s):
    
        
        s = s.strip()
        psr = re.compile('[f|psr|n|u|m]?[M|l|%]$')

        unit_s = ''
    
        if psr.search(s):
            unit_s = psr.search(s).group()
        
        expr = s[0:-len(unit_s)]
                
        self.unit = ''
        self.mult = ''
        
        for c in self.MULTS:
            if c in unit_s:
                self.mult = c
                
        for c in self.UNITS:
            if c in unit_s:
                self.unit = c

        self.value = float(expr) * self.MULTS[self.mult] * self.UNITS[self.unit]
                
        
class V(UnitScalar):
    UNITS = {'l' : 1.0}
    pass

class C(UnitScalar):    
    UNITS = { 'M' : 1.0, '%' : 0.01 }
    pass
