'''
Created on 05.05.2014

@author: jan-hendrikprinz

Constructs a set of tokens to be used to interprete ThermoFisher momentum processes and experiments
'''

import re
import string

class Token:
    '''
    A string token that contains a regular expression to find a string part and a function that can process the returned results.
    '''
    def __init__(self, name, regex, rule):
        self.name = name
        self.needle = regex
        self.rule = rule
        
    def apply(self, s):
        '''
        Apply the token to a string
        
        Parameters
        ----------
        
        s : string
            string the rule function should be applied to
        '''
        return self.rule(self.needle, s)
        
def _xml_rule_equal(needle, s):
    s = re.sub(needle, '<set key = \'\\1\' value = \\2 />', s)
    return s

def _xml_rule_foreach(needle, s):
    find = re.search(needle, s)
    ident = find.group(2)
    attributes = find.group(4)
    content = find.group(5)
    other_id = find.group(3)
    
    attr = string.split(attributes, ",")

    tag = 'foreach'
    ret = '<foreach>'
    
    conts = ident 
    if other_id is not None:
        conts = conts + other_id
                    
    ret += '<containers>'
    for a in string.split(conts, ','):
        ret += "<container id='" + a.strip() + "' />"
        
    ret += '</containers>'
        
    ret += '<parameters>'
    for a in attr:
        sp = string.split(a, "=")
        ret += "<param key='" + sp[0].strip() + "' value=" + sp[1].strip() + "/>"
        
    ret += '</parameters>'

    ret += "<content>"
    
    ret += content
        
    ret += '</content>'

    ret += '</' + tag + '>'
    
    return ret

def _xml_rule_lock(needle, s):
    find = re.search(needle, s)
    var = find.group(1)
    content = find.group(2)        
        
    tag = 'lock'
    ret = '<lock>'
                            
    ret += '<parameters>'
    ret += '<param key="Variable" value="' + var + '"/>'
        
    ret += '</parameters>'
    ret += "<content>"
    
    ret += content
        
    ret += '</content>'
    ret += '</' + tag + '>'
    
    return ret
    
def _xml_rule_command(needle, s):
    find = re.search(needle, s)
    device = find.group(1)
    action = find.group(6)
    ident = find.group(3)
    attributes = find.group(7)
    content = find.group(8)
    other_id = find.group(4)
    
    
    is_action = False
    is_item = False
    
    if (action is not None):
        is_action = True
        
    if (ident is not None):
        is_item = True
        
    tag = ''
    ret = ''
    
    attr = string.split(attributes, ",")
      
    if (device == 'delay'):  
        tag = 'flow'
        ret = "<flow action='delay'"
    elif (device == 'wait_until'):  
        tag = 'flow'
        ret = "<flow action='wait_until'"
        attr.insert(0, "DateTime=" + ident)
    elif (device == 'comment'):
        tag = 'flow'
        key = 'Comment'
        ret = "<flow action='comment'"
    elif (device == 'acquire'):
        tag = 'flow'
        key = 'Variable'
        ret = "<flow action='acquire'"
    elif (is_action is True):
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
        
    if (is_item is True and other_id is not None):
        ret += '<optional>'
        for a in string.split(ident + other_id, ','):
            ret += "<container id='" + a.strip() + "' />"
            
        ret += '</optional>'
        
    ret += '<parameters>'
    
    if ('=' not in attributes):
        ret += '<param key="' + key + '" value="' + attributes.strip() + '" />'
    else:    
        for a in attr:
            sp = string.split(a, "=")
            ret += "<param key='" + sp[0].strip() + "' value=\"" + sp[1].strip() + "\"/>"
        
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
 
def _xml_rule_string(needle, s):
    s = string.replace(s, '<', '&lt;')
    s = string.replace(s, '>', '&gt;')
    s = string.replace(s, '&', '&amp;')
    s = string.replace(s, '"', '&quot;')
    s = s[0] + string.replace(s[1:-1], "'", '&apos;') + s[-1]
#    s = string.replace(s, '\\\\', '\\')
    return s
       
def _xml_rule_comment(needle, s):
#    s = re.sub(needle, '', s)
    s = re.sub(needle, '<comment>\\2</comment>', s)
    return s    
    
def _xml_rule_if(needle, s):
    s = re.sub(needle, '<if condition = \\1><true>\\2</true><false>\\3</false></if>', s)
    return s

def _xml_rule_group(needle, s):
    find = re.search(needle, s)
    if (find.group(2) != ''):
        s = re.sub(needle, '<\\1 id=\'\\2\'>\\3</\\1>', s)
    else:
        s = re.sub(needle, '<\\1>\\3</\\1>', s)
        
    return s

tok_equal = Token('equal', 'set[\\s]+([\\w]+)[\\s]+=[\\s]+([\\w_\'"]+)[\\s]+;', _xml_rule_equal )
tok_foreach = Token( 'foreach', 'foreach [\\s]*(([\\w]+)?(, [\\w]+)*)[\\s]*\\(([\\w\\s=,]+)\\)\\n[\\s]*\\{([^\\{\\}]+)\\}', _xml_rule_foreach )
tok_lock = Token( 'lock', 'lock [\\s]*\\(([\\w\\s]*)\\)\\n[\\s]*\\{([^\\{\\}]+)\\}', _xml_rule_lock )
tok_command = Token( 'command', '([\\w_]+)[ ]*(([\\w]+)?(, [\\w]+)*)[\\s]*((\\[[\\w ]+\\])?)[\\s]*\\(([\\w\\s=,$]+)\\)\\s*([\\w, \\s]*);', _xml_rule_command )
tok_string = Token('string', '\'(([~\\w \\(\\):;,-\\./<>\%$+"]|\\\\\'|\\\\)*?)\'', _xml_rule_string )
tok_comment = Token('comment', '(// (.+))', _xml_rule_comment )
tok_if = Token( 'if', 'if \\(([\\w]+)\\)[\\s ]*\\{([^\\{]*?)\\}[\\s]*else[\\s]*\\{([^\\{]*?)\\}', _xml_rule_if )
tok_group = Token( 'group', '([\\w_]+[ ]?)([\\w]*)[\\s]*\\{([^\\{\\}]+)\\}', _xml_rule_group )

all_token = [
     tok_comment,
     tok_string,
     tok_equal,
     tok_command,
     tok_if,
     tok_foreach,
     tok_lock,
     tok_group
]