'''
Created on 27.07.2014

@author: jan-hendrikprinz
'''

from lxml import etree

import string
import re

# TODO: Clean up

class NSXPathUtil(object):
    '''Mixin that provides methods to simplify xpath handling with namespaces

    '''

    def _untokenize (self, s):
        for psr in reversed(self.tokenlist):
            (key, value) = psr
            s = string.replace(s, key, value)
        return s    

    def _tokenize(self, s):
        self.tokenlist = []
        needle = '\'([\\w @\\\\:;,(\\\\\')-./<>\%"]*?)\''
        name = 'str'
        prog = re.compile(needle)
   
        cc = 0
        while (prog.search(s) is not None and cc < 10000):   
            found = prog.search(s).group(0)
            key = name + str(cc)
            self.tokenlist.append( (key, found) )
            s = prog.sub(key , s, count=1)
            cc += 1
            
        return s                        
    
    def _node_add_ns(self, n):
        if self.namespace is not '' and n!= '':  
            if n != '' and n[0]!='@':
                return self.ns + ':' + n
            else:
                return n
        else:
            return n
            
    def _xpath_add_ns(self, xp):
        if self.namespace is not '':  
            parts = xp.split('/')
            parts = [ self.ns + ':' + psr if psr != '' and psr[0]!='@' else psr for psr in parts]
        
            return '/'.join(parts)
        else:
            return xp
        
    def _wrapxpath(self, xp):      
        if self.namespace is not '' and self.addns:  
            parts = xp.split('/')
            parts = [ self.ns + ':' + psr if psr != '' and psr[0]!='@' else psr for psr in parts]
        
            return '/'.join(parts)
        else:
            return xp
        
    def _xp_fnc(self, xpath):
        '''Construct an XPath object with or without namespace
        '''
        if self.namespace is '':
            return etree.XPath(xpath)
        else:
            return etree.XPath(xpath, namespaces = {self.ns : self.namespace})    

    def _xpath(self, xp):
        if self.namespace is '':
            return self.xobj.xpath(xp)
        else:
            return self.xobj.xpath(xp, namespaces = { self.ns : self.namespace })
    

    def fnc(self, xpath):
        '''Construct an XPath object with or without namespace
        '''
        def wrap(xpath):
            
            xpath = self._
        
            if self.namespace is '':
                return etree.XPath(xpath)
            else:
                return etree.XPath(xpath, namespaces = {self.ns : self.namespace})
        
    def _init_xpath_search(self):
        self.tokenlist = []
        self.xp = self._tokenize(self.xp)
        parts = self.xp.split('/')
        var_parts = {}
        current_xpath = ''
        var_funcs = {}
        
        for part in parts[1:]:
            sides = part.split('?')
            sides[0] = self._node_add_ns(sides[0])

            sides[0] = self._untokenize(sides[0])
                
            if len(sides) > 1:
                sides[1] = self._untokenize(sides[1])
                for var in sides[1].split('&'):
                    spl = var.split('=')
                    var_name = spl[0]
                    node = (sides[0].split('['))[0]
                    spl[1] = string.replace(spl[1], "'", "", )
                    assign = current_xpath + '/' + node + '/' + spl[1]
                    var_parts[var_name] = assign
                    var_funcs[var_name] = etree.XPath(assign)
        
            current_xpath += '/' + self._untokenize(sides[0]) 
        
        self.xpath = current_xpath
        self.vars = var_parts
        self.var_fnc = var_funcs
        self.filter_fnc = etree.XPath(self.xpath)