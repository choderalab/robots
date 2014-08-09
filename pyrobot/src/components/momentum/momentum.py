'''
Created on 27.04.2014

@author: JH Prinz
'''

import converter as cv

import components.momentum.momentum_templates as sc
        
class SimpleGetItem:
    def __getitem__(self, index):
        out = self.data
        for path in index.split('/'):
            if (type(out) is dict):
                out = out[path]
            elif (type(out) is list):
                if (path.isdigit()):
                    out = out[int(path)]
                else:
                    out = [i for i in out if i['id'] == path][0]
        return out
    
    def __setitem__(self, index, value):        
        out = self.data
        way = index.split('/')
        last = way[-1]
        way.pop()
        for path in way:
            if (type(out) is dict):
                out = out[path]
            elif (type(out) is list):
                if (path.isdigit()):
                    out = out[int(path)]
                else:
                    out = [i for i in out if i['id'] == path][0]

        if (type(out) is dict):
            out[last] = value
        elif (type(out) is list):
            if (last.isdigit()):
                out[int(last)] = value
            else:
                pos = [no for no, i in enumerate(out) if i['id'] == last][0]
                out[pos] = value

class MStep(SimpleGetItem):
    def __init__(self, d = {}):
        self.data = d

        
class Parser(SimpleGetItem, sc.MomentumFactory):    
    def __init__(self):
        self.tokenlist = []
        self.name = ''
        self.data = {}
        
    @staticmethod
    def fromMomentum(s):
        obj = Parser()
        obj.momentum = s
        obj.xml = cv.momentum_to_xml(obj.momentum)
        obj.data = cv.xml_to_python(obj.xml)
        obj.momentum = cv.python_to_momentum(obj.data)
        return obj
    
    @staticmethod
    def fromXML(s):
        obj = Parser()
        obj.xml = s
        obj.data = cv.xml_to_python(obj.xml)
        obj.momentum = cv.python_to_momentum(obj.data)
        obj.xml = cv.momentum_to_xml(obj.momentum)
        return obj
    
    @staticmethod
    def fromPython(d):
        obj = Parser()
        obj.data = d
        obj.momentum = cv.python_to_momentum(obj.data)
        obj.xml = cv.momentum_to_xml(obj.momentum)
        obj.data = cv.xml_to_python(obj.xml)
        return obj
    
    def asMomentum(self):
        return cv.python_to_momentum(self.data)

    def asPython(self):
        return self.data

    def asXML(self):
        return cv.momentum_to_xml(self.asMomentum())

    @staticmethod
    def readMomentum(filename):
        with open (filename, "r") as myfile:
            return Parser.fromMomentum(myfile.read())

    @staticmethod
    def readXML(filename):
        with open (filename, "r") as myfile:
            return Parser.fromXML(myfile.read())
        
    def toMomentumFile(self, filename):
        outfile = open(filename, 'w')
        outfile.write(self.asMomentum())
        outfile.close()
        
    def toXMLFile(self, filename):
        outfile = open(filename, 'w')
        outfile.write(self.asXML())
        outfile.close()
        
    # UTILITY FUNCTIONS TO EDIT THE PYTHON REPRESENTATION
    #
    # might be replaced by something that only works on the xml scheme
    # for now this is easier
    
    def process_variables(self):
        variables = self['process/variables']
        return { v['id'] : v['type'] for v in variables }

    def profile_variables(self):
        variables = self['process/variables']
        return { v['id'] : v['type'] for v in variables }
    
    def variables(self):
        return dict(self.process_variables(), **(self.profile_variables()))
    
    def add_variable(self, var, var_type = 'String'):
        variables = self['process/variables']
    
        if var not in self.variables():
            variables.append(self.momentum_variable(var, var_type))     
        
        self['process/variables'] = variables
        
    # CONVENIENCE ACCESSORS
    
    def clearsteps(self):
        self.steps = []

    @property
    def steps(self):
        return self['process/steps']
    
    @steps.setter
    def steps(self, value):
        self['process/steps'] = value

    @property
    def containers(self):
        return self['process/containers']
    
    @containers.setter
    def containers(self, value):
        self['process/containers'] = value
        
