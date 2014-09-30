'''
Created on 14.04.2014

@author: jan-hendrikprinz
'''

import re

def replace_value(s, key, val, val_min, val_max):
    
    if val_min < val_max:
        val_percent = 1.0 * (val - val_min) / (val_max - val_min)
    else:
        val_percent = 1.0
    
    s = s.replace( '{' + key + '}', str(val))
    s = s.replace( '{%(' + key + ')}', str(val_percent))
    
    return s

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
    
def _interprete_well(el, size= [8, 12]):
    if type(el) is int:
        return WellToPosition(size, el)
    if type(el) is list:
        return el
    else:
        return NameToPosition(el)

def _to_expression(s):
    
    s = s.strip()
    psr = re.compile('[f|psr|n|u|m]?[M|l|%]$')
    
    unit = psr.search(s).group()
        
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
    for psr in range(0,8):
        if (2**psr) & i > 0:
            l.append(psr+1)
    return l
    
def _interprete_heads(s):

    ll = []

    if type(s) is str:
        ll = _interprete_rangestring(s)
    
    if type(s) is list:
        
        ll = [_interpret_head(psr) for psr in s]
        
    return sum([_headToNumber(psr) for psr in ll])
