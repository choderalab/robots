'''
Created on 04.08.2014

@author: jan-hendrikprinz
'''

import re

class ContainerFactory(object):
    '''
    A mixin that allows to initialize a container using the docstring specifications and other util related to that
    '''

    def _construct(self, *initial_data, **kwargs):
        
        # Defaults

        self.att_type = {}
        self.att_doc = {}
        self.att_default = {}
        self.att_optional = {}
        self.att_opts = {}
        self.att_unit = {}
        self.att = []
        self.att_computed = {}

        
        str_template = ''

        filename = 'definition.md'
        with open (filename, "r") as myfile:
            str_template = myfile.read()   

                        
        new_attr = True;
        this_attr = ''
        self.gen_str = ''
        self.gen_str_prop = ''
        def_fnc = str
        
        
        for line in str_template.split('\n'):
            ignore = False
            if line.strip() == '':
                # empty
                new_attr = True
                ignore = True
            else:            
                if line[0] == '#':
                    # comment -> ignore
                    ignore = True
            
            if not ignore:
                if new_attr == False:
                    line = line.strip()
                    if hasattr(self.att_doc,this_attr):
                        self.att_doc[this_attr] += "\n" + line
                    else:
                        self.att_doc[this_attr] = line
                    
                if line[0:4] == '    ':
                    #
                    new_attr = False
                    spl = line.split(':')
                    name = spl[0].strip()
                    self.att.append(name)
                    this_attr = name
                    computed = False
                    
                    if len(spl) > 1:
                        type_str = spl[1].strip()                
                        type_name = type_str.split(' ')[0].lower()
                        
                        self.att_type[name] = type_name
                        
                        if '(optional)' in type_str:
                            # mark as optional
                            self.att_optional[name] = True
                        
                        if '(computed)' in type_str:
                            # needs to be implemented
                            computed = True
                            self.att_computed[name] = True
                        else:
                            self.att_computed[name] = False
                            
                        found = re.search( '\\[(.*)?\\]', type_str)
                        
                        if found is not None:
                            found = found.group(1)
                            self.att_unit[name] = found
#                            print name + 'unit : ' + found

                        def_val = ''
                        def_fnc = str

                        if type_name == 'int':
                            def_val = '0'
                            def_fnc = int

                        if type_name == 'float':
                            def_val = '0.0'
                            def_fnc = float

                        if type_name == 'bool':
                            def_val = 'False'
                            def_fnc = bool
                        
                        if type_name == 'enum':
                            found = re.search( '\\{(.*)?\\}', type_str)
                            
                            if found is not None:
                                found = found.group(1)
                                opts = found.split(',')
                                opts = [ o.strip() for o in opts]
                                self.att_opts[name] = opts

                        found = re.search( '\\(\\w*?default\\w*?=(.*)?\\)', type_str)
                        
                        if found is not None:
                            found = found.group(1)
                            def_val = found
                        
                        if type_name == 'enum':
                            found = re.search( '\\{(.*)?\\}', type_str)
                            
                            if found is not None:
                                found = found.group(1)
                                opts = found.split(',')
                                opts = [ o.strip() for o in opts]
                                self.att_opts[name] = opts
                                
                        def_val = def_fnc(def_val)
                        
                        self.att_default[name] = def_val

                    if def_fnc is str:
                        def_val = "'" + def_val + "'"
                    else:
                        def_val = str(def_val)

                    if not computed:
                        setattr(self, name, '')
                        self.gen_str += 'self.' + name + " = %s\n" % def_val
                        
                    else:
                        self.gen_str_prop += '\n@property\n'
                        self.gen_str_prop += 'def %s (self):\n' % name
                        self.gen_str_prop += "    %s = '%s'\n" % (name, def_val)
                        self.gen_str_prop += '    return %s\n' % name
                                    
    def help(self, s):
        return self.att_doc[s]
    
    def _gen_html_query(self, s):
        ret = ''
        oldgroup = ''
        for name in self.att:
            line = ''            
            if oldgroup != name.split('_')[0]:
                if oldgroup != '':
                    line += '</div>\n'
                oldgroup = name.split('_')[0]              
                line += '<div class="panel-heading"><p>%s</p></div>\n<div class="panel-body">\n' % oldgroup
                
            sname = '_'.join(name.split('_')[1:])
            type = self.att_type[name]
            line += '<div class="form-group">\n'
            line += '<label class="control-label col-sm-3">%s</label>\n' % sname
            
            popover = 'data-toggle="popover" data-placement="top" data-original-title="%s" data-content="%s" data-trigger="hover"' % (name, self.att_doc[name])
            popover = 'title="%s" data-toggle="tooltip" data-trigger="hover"' % self.att_doc[name]
            
            if type=='string':
                line += '<div class="input-group col-sm-4">\n'
                line += '<input data-bind="value: %s" id="%s" type="text" placeholder="%s" class="form-control tooltips" %s/>\n' % (name, name, name, popover)
            elif type=='url':
                line += '<div class="input-group col-sm-4">\n'
                line += '<input data-bind="value: %s" id="%s" type="text" placeholder="%s" class="form-control tooltips" %s/>\n' % (name, name, name, popover)
            elif type=='int':
                line += '<div class="input-group col-sm-4">\n'
                line += '<input data-bind="value: %s" id="%s" type="text" placeholder="%s" class="type-int form-control tooltips" %s/>\n' % (name, name, name, popover)
            elif type=='float':
                line += '<div class="input-group col-sm-4">\n'
                line += '<input data-bind="value: %s" id="%s" type="text" placeholder="%s" class="type-float form-control tooltips" %s/>\n' % (name, name, name, popover)
            elif type=='custom':
                line += '<div class="input-group col-sm-4">\n'
                line += '<input data-bind="value: %s" id="%s" type="text" placeholder="%s" class="form-control tooltips" %s/>\n' % (name, name, name, popover)
            elif type=='enum':
                line += '<div class="input-group col-sm-4">\n'
                line += '<select data-bind="chosen: {%s}, value: %s" id="%s" data-placeholder="Please select..." class="form-control chosen-select" >\n' % (', '.join([ "'" + a + "' : '" + a + "'" for a in self.att_opts[name]]), name, name)
#                line += '<option value=""> </option>\n'
#                for opt in self.att_opts[name]:
#                    line += '<option value="%s">%s</option>\n' % (opt, opt)
#                
                line += '</select>\n'
            elif type == 'bool':
#                line += '<div class="ckbox ckbox-success">\n'
#                line += '<input data-bind="checked: %s" type="checkbox" id="%s" checked="checked" />\n' % (name, name)
#                line += '<label for="dinnerThu">Donnerstag</label>'
#                line += '</div>\n'

                line += '<div class="col-sm-8 control-label">\n'
                line += '<div data-bind="toggle: %s" class="toggle-primary"></div>\n' % name
                
            if name in self.att_unit:
                line += '<span class="input-group-addon">%s</span>\n' % self.att_unit[name]
                
#            line += '<span class="help-block"><small>%s</small></span>\n' % self.att_doc[name]

                
            line += '</div>\n'      

            line += '</div>\n'      
            line += '\n'      
            
            if not self.att_computed[name]:
                ret += line
        
        ret += '</div>\n'
                
        return ret

    def _gen_knockoutvars(self):
        ret = ''
        for name in self.att:
            line = ''            
            
            line += 'self.' + name + ' = ko.observable(\'' + str(self.att_default[name]) + '\');\n'

            if not hasattr(self.att_optional, name):
                ret += line
                        
        return ret

    def _gen_mysql_createtable(self, name):
        ret = 'CREATE TABLE ' + name + ' (\n'
        vs = ['id INT NOT NULL AUTO_INCREMENT PRIMARY KEY']
        for att in self.att:           
            ty = self.att_type[att];
            s  = ''
            s += att
            ty = ''
            mysql_type = 'VARCHAR(255)'
            if ty == 'float':
                mysql_type = 'FLOAT'
            elif ty == 'int':
                mysql_type = 'INT'
            elif ty == 'bool':
                mysql_type = 'BOOL'
            s += ' ' + mysql_type
            vs.append(s)
        
        ret += ',\n'.join(vs)
        ret += '\n);'
        
        return ret
