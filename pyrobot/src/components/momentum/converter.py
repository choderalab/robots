'''
Created on 27.04.2014

@author: JH Prinz
'''

import re
import string
from lxml import etree
from jinja2 import Environment, PackageLoader
import datetime
from token import ALLTOKEN

def _tokenize(tokenlist, s):
    for token in ALLTOKEN:
        prog = re.compile(token.needle)

#        print s
        cc = 0
        while (prog.search(s) is not None and cc < 10000):   
            
            found = prog.search(s).group(0)
            
            key = token.name + str(cc)
            
            tokenlist.append( (token, key, found) )
            
            s = prog.sub(key , s, count=1)
            cc += 1
    return s        

def _untokenize (tokenlist, s):
    for psr in reversed(tokenlist):
        (token, key, value) = psr
        s = string.replace(s, key, value)
    return s
               

def _apply_token(tokenlist):
    for index, psr in enumerate(tokenlist):
        (token, key, value) = psr
        value = token.apply(value)            
        tokenlist[index] = (token, key, value)
        

def _get_parameters(root, path = ""):
    return { 
        element.attrib['key'] : element.attrib['value'] 
        for element in root.xpath(path + "parameters/*")  
    } 
    

def _get_containers(root, path = ""):
    return [
        element.attrib
        for element in root.xpath(path + "containers/*")  
    ]
    

def _get_item(root, path = ""):
    cont = {}
    cont['params'] = _get_parameters(root, "")
    cont['containers'] = _get_containers(root, "")
    for key, value in root.attrib.iteritems():
        cont[key] = value
    return cont


def _do_step(node):
    if node.tag == 'parallel':
        return { 'type' : 'parallel', 'branches' : [ _walk_steps(psr) for psr in node.xpath('branch')]}
    elif node.tag == 'if':
        return { 'type' : 'if', 'condition' : node.attrib['condition'], 'true' : _walk_steps(node.xpath('true')[0]), 'false' :_walk_steps(node.xpath('false')[0])}
    elif node.tag == 'lock':
        param = _get_parameters(node, "")
        return { 'type' : 'lock', 'var' : param['Variable'], 'content' : _walk_steps(node.xpath('content')[0]) }
    elif node.tag == 'foreach':  
        return { 'type' : 'foreach', 'containers' : _get_containers(node, ""), 'params' : _get_parameters(node, ""), 'content' : _walk_steps(node.xpath('content')[0]) }
    elif node.tag == 'flow':
        return { 'type' : 'flow', 'action' : node.attrib['action'], 'params' : _get_parameters(node, "") }
    elif node.tag == 'set':
        return { 'type' : 'set', 'key' : node.attrib['key'], 'value' : node.attrib['value']}
    else:
        return dict( {'type' : 'step' }, **_get_item(node, ""))


def _walk_steps(root):
    return [
            _do_step(node)
            for node in root
            ]        
        

def momentum_to_xml(s):
    tokenlist = []
    s = re.sub('(\\S) // (.+)', '\\1', s)

    s = _tokenize(tokenlist, s)
    
    _apply_token(tokenlist)
    s = _untokenize(tokenlist, s)
    s = string.replace(s, '\t', '  ')    
    s = "<document>\n" + s + "\n</document>"
    return s

def xml_to_momentum(s):
    return python_to_momentum(xml_to_python(s))

def xml_to_python(s):
    root = etree.XML(s)

    profile = root.xpath("/document/profile")[0]
    process = profile.xpath("process")[0] 
    
    profile_id = profile.attrib['id']
    
    profile_runtime = {
        'params' : _get_parameters(profile, 'runtime/')
    }
    
    profile_devices = [
        _get_item(item, "") for item in profile.xpath("devices/*")  
    ]
    
    profile_pools = [
        _get_item(item, "") for item in profile.xpath("pools/*")  

    ]
    
    profile_variables = [
        _get_item(item, "") for item in profile.xpath("variables/*")  
    ]
    
    process_id = process.attrib['id']
    
    process_variables = [
        _get_item(item, "") for item in process.xpath("variables/*")  
    ]
    
    process_containers = [
        _get_item(item, "") for item in process.xpath("containers/*")  
    ]
    
    steps = process.xpath("*[contains(., 'steps')]/following-sibling::*")
    process_steps = _walk_steps(steps)
    
    return {
            'date' : datetime.datetime.now(),
            'profile' : {
                         'id' : profile_id,
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
        
def python_to_momentum(d):
    env = Environment(loader=PackageLoader('components', 'momentum/templates/process'))
    
    def format_datetime(value, format='auto'):
        if format == 'auto':
            format="%A, %B %d, %Y %I:%M:%S %psr"
        return value.strftime(format)
    
    env.filters['datetime'] = format_datetime
    
    template = env.get_template('plate_type_analysis.mpr')
    
    result = template.render(data = d)
    
#    result = string.replace(, '\\', '\\\\')

    return result
