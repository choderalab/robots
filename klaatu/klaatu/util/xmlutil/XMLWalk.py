'''
Created on 27.07.2014

@author: Jan-Hendrik Prinz
'''

import copy

from util.xmlutil.NSXPathUtil import NSXPathUtil

class XMLAnalyzer(object):
    def __init__(self):
        self.result = []
        self._init()
        
    def store(self, tree):
        '''Stores the result from apply in the `self.result` member variable
        '''
        
        result = self.apply(tree)
        if result is not None:
            self.result.append(result)
            return True
        else:
            return False
            
    def fnc(self):
        '''Returns a function that calls the class' store function given a tree parameter
        
        Notes
        -----
        
        This is to be used in XMLWalker
        '''

        def saver(root, find_only = False):
            if find_only:
                return self.apply(root, True)
            else:
                return self.store(root)
            
        return saver

    def apply(self, tree, find_only = False):
        '''Apply to a (reduced) tree and return the result
        
        Paramters
        ---------
        
        tree : lxml.Tree
            The tree to be checked. Only the first found element is treated
        find_only : bool
            If set to true results are not added or scanned for. The return result just returns
        
        
        Notes
        -----
        
        This is a stub. Needs to be overwritten by the actual implementation
        '''
        return None

class XPathAnalyzer(XMLAnalyzer, NSXPathUtil):
    '''A XMLAnalzer that takes a XPathSearch string and if in the given tree a matching xpath is present the specified variables as a python dictionary
    
    Examples
    --------
    
    The line below creates an analyzer that looks for all DataNode nodes in the XMLTree and returns a dict
        
    >>> xmlutil = '<Data key="name" value="Joe" /><Data key="age" value="25" />'
    >>> analyzer = XPathAnalyzer('//Data?ky=@key&vl=@value')
    >>> walker = XMLWalker(xmltree)
    >>> result = walker.walk(analyzer)
    [ { 'ky' : 'name', 'vl' : 'Joe' }, { 'ky' : 'age', 'vl' : '25' } ]
    
    Todo
    ----
    
    Use precompiled xpath functions to speed up using `call_fnc = etree.XPath(xpath_string)`
    '''
    def __init__(self, s, namespaces = { 'ns' : '' }, addns = True):
        self.xp = s
        self.xpath = ''
        self.tokenlist = []    
        self.namespace = namespaces.values()[0]
        self.ns = namespaces.keys()[0]
        self.addns = addns
        self.non_existent = None
        self.custom_type = {}

        super(XPathAnalyzer, self).__init__()        
        
    def _parse_type(self, val, typ = None):
        if typ is not None:
            if typ in self.custom_type:
                return self.custom_type[typ](val)
            elif typ == 'str':
                return str(val)
            elif typ == 'int':
                return int(val)
            elif typ == 'float':
                return float(val)
            elif typ == 'bool':
                return bool(val)
            else:
                return val
        else:
            return val
        
    def add_custom_type(self, name, func):
        self.custom_type[name] = func
                
    def _init(self):
        self._init_xpath_search()

    def apply(self, tree, find_only = False):
        if self.namespace is '':
            r = tree.xpath(self.xpath)
        else:
            r = tree.xpath(self.xpath, namespaces = { self.ns : self.namespace })
            
        if find_only:
            return len(r) > 0
        else:
            if len(r) > 0:
                if self.namespace is '':
                    ret = {}
                    for key, psr in self.vars.iteritems():
                        res = tree.xpath(psr)
#                        print len(res)
                        if len(res) > 0:                        
                            ret[key] = self._parse_type(res[0], self.type_fnc[key])
                        else:
                            ret[key] = self.non_existent
                            
                    return ret
                else:
                    ret = {}
                    for key, psr in self.vars.iteritems():
                        res = tree.xpath(psr, namespaces = { self.ns : self.namespace })
                        if len(res) > 0:                        
                            ret[key] = self._parse_type(res[0], self.type_fnc[key])
                        else:
                            ret[key] = self.non_existent
                            
                    return ret                    
            else:
                return None
            
class XMLWalker(object):        
    '''Utility class to walk over all nodes of a tree and allow fast access to the reduce tree that only contains the actual node and all ancestors
    
    '''

    def __init__(self, xobj):
        '''Initialize the class with the objectify object `xobj`
    
        Parameters
        ----------
        xobj : lxml.objectity
            The tree to be traversed
        
        '''

        self.tree = None
        self.xobj = xobj    
        self.tree = copy.deepcopy(self.xobj)        
        XMLWalker._removechildren(self.tree)            

    @staticmethod
    def _removechildren(node):
        for c in node.getchildren():
            node.remove(c)        
    
    @staticmethod
    def _run_children(root, buildtree, recursivetree, fnc):
        if fnc(root, find_only = True):
            # this is a node we are interested in, so add the rest of the children to allow them also to be screened
            child_list = []
            for child in buildtree.iterchildren():
                add = copy.deepcopy(child)
                child_list.append(add)
                recursivetree.append(add)
                
            # Here we have the complete stuff
            
            fnc(root)
            
            # And remove to continue

            for child in child_list:
                recursivetree.remove(child)
            
        else:
            for child in buildtree.iterchildren():
                add = copy.deepcopy(child)
                XMLWalker._removechildren(add)
                recursivetree.append(add)
                XMLWalker._run_children(root, child, recursivetree.getchildren()[0], fnc)
                recursivetree.remove(add)
    
    def _walktree(self, fnc):
        XMLWalker._run_children(self.tree, self.xobj, self.tree, fnc)
        
    def walk(self, analyzer):
        '''Walk the tree and run `analyzer` at each node and return the result
        
        Parameters
        ----------
        
        analyzer : XMLAnalyzer
            instance that take a reduced tree and stores results. After the traversal the results are accesible within the analyzer using `analyzer.result`
         
        '''
        self._walktree(analyzer.fnc())
        
        return analyzer.result