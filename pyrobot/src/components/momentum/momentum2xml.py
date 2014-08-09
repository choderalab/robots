'''
Created on 27.04.2014

@author: JH Prinz
'''

# 1. Tokenize all comments using '\n[^\n]*//(.+)' into comment_######
# 2. Tokenize all strings using '([\w \\:;,(\\')-.<>\%"])*' into string_######
# 3. Tokenize all equal statements using set[\s]+([\w]+)[\s]+=[\s]+([\w_'"])+[\s]+; into equal_#####
# 4. Tokenize all expression using '[\w]+[ ]*([\w]+)?[\s]+(\[[\w ]+\])?[\s]*\([\w\s=',/:"\\\.<>()\[\]\-\%\+]+\)\s*[\w, '\(\)_\s]*;' into expr_###### that are later parsed into XML
# 5. Tokenize all if-statements using if \('[\w>]+'\)[\s ]*\{([^\{]*?)\}[\s]*else[\s]*\{([^\{]*?)\} into if_######
# 6. Tokenize all groups using [\w]+([ ]+[\w]+)?\n[\s]*\{[^\{]*\} into group_######

import re
import string
from lxml import etree
from jinja2 import Environment, PackageLoader
import datetime

class Token:
    def __init__(self, name, regex, rule):
        self.name = name
        self.needle = regex
        self.rule = rule
        
    def apply(self, s):
        return self.rule(self.needle, s)
        
def _xml_rule_equal(needle, s):
    s = re.sub(needle, '<set key = \'\\1\' value = \\2 />', s)
    return s
tok_equal = Token('equal', 'set[\\s]+([\\w]+)[\\s]+=[\\s]+([\\w_\'"]+)[\\s]+;', _xml_rule_equal )
    
def _xml_rule_command(needle, s):
    find = re.search(needle, s)
    device = find.group(1)
    action = find.group(5)
    ident = find.group(3)
    attributes = find.group(6)
    content = find.group(7)
    
    attr = string.split(attributes, ",")
    is_action = False
    is_item = False
    
    if (action is not None):
        is_action = True
        
    if (ident is not None):
        is_item = True
        
    tag = ''
        
    if (is_action is True):
        tag = 'step'
        ret = '<step ' + 'device=\'' + device +'\''
        ret += ' action=\'' + action + '\''
    elif (is_item is True):
        tag = 'item'
        ret = '<item ' + 'type=\'' + device + '\' id=\'' + ident + '\'' 
    else:
        tag = device
        ret = '<' + device
        
    if (action is not None):
        is_action = True
        
    ret +=  ' >'
        
    ret += '<parameters>'
    for a in attr:
        sp = string.split(a, "=")
        ret += "<param key='" + sp[0].strip() + "' value=" + sp[1].strip() + "/>"
        
    ret += '</parameters>'

        
    if (content.strip() != ''):
        ret += "<containers>"
        sp = string.split(content, ",")
        for part in sp:
            c = string.split(part.strip(), " ")
            ret += '<container id=\'' + c[0] + '\''
            
            if ('in' in c):
                ind = c.index('in')

                if (ind == 2):
                    ret += ' lid=' + c[ind - 1]                
                
                ret += ' in=' + c[ind + 1]
                
            if ('ends' in c):
                ind = c.index('ends')
                ret += ' ends=' + c[ind + 1]
            
            ret += ' />'
            
        ret += '</containers>'

    ret += '</' + tag + '>'

    return ret

tok_command = Token( 'command', '([\\w]+)[ ]*(([\\w]+)?)[\\s]*((\\[[\\w ]+\\])?)[\\s]*\\(([\\w\\s=,]+)\\)\\s*([\\w, \\s]*);', _xml_rule_command )
        
    
def _xml_rule_string(needle, s):
    s = string.replace(s, '<', '&lt;')
    s = string.replace(s, '>', '&gt;')
    s = string.replace(s, '&', '&amp;')
    s = string.replace(s, '\\\\', '\\')
    return s 
   
tok_string = Token('string', '\'([\\w \\\\:;,(\\\\\')-./<>\%"]*?)\'', _xml_rule_string )
    
def _xml_rule_comment(needle, s):
    s = re.sub(needle, '<comment>\\1</comment>', s)
    return s    

tok_comment = Token('comment', '// (.+)', _xml_rule_comment )
    
def _xml_rule_if(needle, s):
    s = re.sub(needle, '<if condition = \\1><true>\\2</true><false>\\3</false></if>', s)
    return s

tok_if = Token( 'if', 'if \\(([\\w]+)\\)[\\s ]*\\{([^\\{]*?)\\}[\\s]*else[\\s]*\\{([^\\{]*?)\\}', _xml_rule_if )

def _xml_rule_group(needle, s):
    find = re.search(needle, s)
    if (find.group(2) != ''):
        s = re.sub(needle, '<\\1 id=\'\\2\'>\\3</\\1>', s)
    else:
        s = re.sub(needle, '<\\1>\\3</\\1>', s)
        
    return s

tok_group = Token( 'group', '([\\w]+[ ]?)([\\w]*)\\n[\\s]*\\{([^\\{\\}]+)\\}', _xml_rule_group )

        
class Parser:
    
    token = [
             tok_comment,
             tok_string,
             tok_equal,
             tok_command,
             tok_if,
             tok_group
             ]
    
    def __init__(self, s):
        self.s = s      
        self.tokenlist = []
        self.input = s
        
    def tokenize(self):
        for token in self.token:
            prog = re.compile(token.needle)
       
            cc = 0
            while (prog.search(self.s) is not None and cc < 10000):   
                
                found = prog.search(self.s).group(0)
                
                key = token.name + str(cc)
                
                self.tokenlist.append( (token, key, found) )
                
                self.s = prog.sub(key , self.s, count=1)
                cc += 1
                
    def untokenize (self):
        for psr in reversed(self.tokenlist):
            (token, key, value) = psr
            self.s = string.replace(self.s, key, value)
                    
    def apply(self):
        for index, psr in enumerate(self.tokenlist):
            (token, key, value) = psr
            value = token.apply(value)            
            self.tokenlist[index] = (token, key, value)
            
    def getParameters(self, root, path = ""):
        return { 
            element.attrib['key'] : element.attrib['value'] 
            for element in root.xpath(path + "parameters/*")  
        } 
        
    def getContainers(self, root, path = ""):
        return [
            element.attrib
            for element in root.xpath(path + "containers/*")  
        ]
        
    def getItem(self, root, path = ""):
        cont = {}
        cont['params'] = self.getParameters(root, "")
        cont['containers'] = self.getContainers(root, "")
        for key, value in root.attrib.iteritems():
            cont[key] = value
        return cont
    
    def do_step(self, node):
        if node.tag == 'if':
            return { 'type' : 'if', 'condition' : node.attrib['condition'], 'true' : self.walk_steps(node.xpath('true')[0]), 'false' : self.walk_steps(node.xpath('false')[0])}
        elif node.tag == 'set':
            return { 'type' : 'set', 'key' : node.attrib['key'], 'value' : node.attrib['value']}
        else:
            return dict( {'type' : 'step' }, **self.getItem(node, ""))
    
    
    def walk_steps(self, root):
        return [
         self.do_step(node)
         for node in root
         ]        
            
    def toXML(self):
        self.tokenlist = []
        self.s = self.input
        self.tokenize()
        self.apply()
        self.untokenize()
        self.s = string.replace(self.s, '\t', '  ')    
        self.s = "<document>\n" + self.s + "\n</document>"
        return self.s
    
    def toPython(self):
        xml_source = self.toXML()
        
        self.root = etree.XML(xml_source)

        self.profile = self.root.xpath("/document/profile")[0]
        self.process = self.profile.xpath("process")[0] 
        
        profile_runtime = {
            'params' : self.getParameters(self.profile, 'runtime/')
        }
        
        profile_devices = [
            self.getItem(item, "") for item in self.profile.xpath("devices/*")  
        ]
        
        profile_pools = [
            self.getItem(item, "") for item in self.profile.xpath("pools/*")  

        ]
        
        profile_variables = [
            self.getItem(item, "") for item in self.profile.xpath("variables/*")  
        ]
        
        process_id = self.process.attrib['id']
        
        process_variables = [
            self.getItem(item, "") for item in self.process.xpath("variables/*")  
        ]
        
        process_containers = [
            self.getItem(item, "") for item in self.process.xpath("containers/*")  
        ]
        
        steps = self.process.xpath("*[contains(., 'steps')]/following-sibling::*")
        process_steps = self.walk_steps(steps)
        
        return {
                'date' : datetime.datetime.now(),
                'profile' : {
                             'runtime' : profile_runtime,
                             'devices' : profile_devices,
                             'pools' : profile_pools,
                             'variables' : profile_variables 
                             },
                'process' : {
                             'id' : process_id,
                             'variables' : process_variables,
                             'containers' : process_containers,
                             'steps' : process_steps
                             }
                }
        
        
        
def PyToMomentum(d):
    env = Environment(loader=PackageLoader('momentum', 'templates/process'))
    
    def format_datetime(value, format='auto'):
        if format == 'auto':
            format="%A, %B %d, %Y %I:%M:%S %psr"
        return value.strftime(format)
    
    env.filters['datetime'] = format_datetime
    
    template = env.get_template('plate_type_analysis.mpr')
    
    return string.replace(template.render(data = d), '\\', '\\\\')
