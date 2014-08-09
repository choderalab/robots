'''
Created on 14.04.2014

@author: jan-hendrikprinz
'''

import util.Units as u

class Mixture:
    'A mixture is a description for a combination of one or more liquids with their respective concentrations'
    def __init__(self, content):
        self.contents = {psr : u.C(content[psr]) for psr in content}
        
    def __str__(self):
        output = ''
        for s in self.contents:
            output += s + ' : ' + str(self.contents[s]) + ", "
            
        return output
        
    def liquids(self):
        return {psr : self.contents[psr] for psr in self.contents if self.contents[psr].type == 'liquid'}
        
    def liquid_names(self):
        return self.liquids().keys()
        
    def compounds(self):
        return {psr : self.contents[psr] for psr in self.contents if self.contents[psr].type == 'compound'}
        
    def all_names(self):
        return self.contents.keys()
        
    def compound_names(self):
        return self.compounds().keys()
        
    def concentrations(self, names):
        return [ self.contents[n].val('') if n in self.contents else 0.0 for n in names ]
