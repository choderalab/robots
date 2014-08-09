'''
Created on 27.07.2014

@author: Jan-Hendrik Prinz
'''

from lxml import objectify

import copy

from xmlutil.XMLBind import XMLBind

class XMLFactory(object):
    def __init__(self):
        pass
    
    def create_from_string(self, s, bindings, namespaces = {'ns' : ''}, addns = True):
        
        binder = XMLBind(objectify.fromstring(s), namespaces, addns)
        
        for name, b in bindings.iteritems():
            binder.bind_attribute(name, b)
        
        def creator(**kwargs):
            
            for key, value in kwargs.iteritems():
                if key in bindings:
                    # binding exists to set the value
                    binder[key] = str(value)
#                else:
#                    print key, 'does not exist'
                
            # need a deep copy otherwise after each new generation all other objects would change as well!!!!
            return copy.deepcopy(binder.xobj)
        
        # return the generating function 
        return creator
        