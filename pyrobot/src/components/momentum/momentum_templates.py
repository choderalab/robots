'''
Created on 05.05.2014

@author: jan-hendrikprinz
'''

class MomentumFactory(object):
    def evo_run_singleplate(self, script, plate_id, start_pos, end_pos):
        return {
                'device': 'EVO', 
                'action': '[RunScript]', 
                'type': 'step', 
                'containers': [{'lid': 'Unlidded', 'ends': end_pos, 'id': plate_id, 'in': start_pos}], 
                'params': {'SetVars': 'No', 'Enabled': 'Yes', 'Comments': '', 'ScriptName': script, 'RunOnAbortedIteration': 'No', 'Result': '', 'Duration': '00:02:00', 'MaximumOperationTime': '00:20:00'}
                }
        
    def centrifuge_spin(self, plate_id, bucket = 'Bucket 1', duration = '00:00:10', velocity = '500'):
        return {
                'device': 'HiG4Centrifuge', 
                'action': '[Spin]', 
                'type': 'step', 
                'containers': [{'id': 'ActivePlate', 'in': 'Bucket 1'}], 'params': {'BucketNumberToLoad': 'Bucket1', 'Enabled': 'Yes', 'AccelerationPercent': '50', 'Comments': '', 'SpinTimeAtCruiseVelocity': duration, 'Duration': duration, 'RunOnAbortedIteration': 'No', 'Result': '', 'SpinGs': velocity, 'DecelerationPercent': '50'}}
    
    def flow_if(self, condition, true_steps, false_steps = []):
        if type(true_steps) is dict:
            true_steps = [true_steps]
            
        if type(false_steps) is dict:
            false_steps = [false_steps]
    
        
        return {
                'type': 'if',
                'condition': condition,
                'true': true_steps,
                'false': false_steps       
                }
        
    def flow_set(self, variable, value):
        return {
                'type': 'set',
                'key': variable,
                'value': value       
                }
        
    def flow_iteration_assign(self, variable, width, values):
        return self.flow_iteration(width, [self.flow_set(variable, psr) for psr in range(width[0], width[1] + 1)])
    
    def flow_iteration(self, width, values):
        left = width[0]
        right = width[1]
        if right == left:
            return values[0]
        else:
            spl = (right - left) / 2
            leftX = self.flow_iteration([left, left + spl ], values[0:spl + 1])
            rightX = self.flow_iteration([left + spl + 1, right ], values[spl + 1:])
            
            if type(leftX) is dict:
                leftX = [leftX]
    
            if type(rightX) is dict:
                rightX = [ rightX ]
    
            return {
                    'type': 'if',
                    'condition': 'Iteration>' + str(spl + left),
                    'false': leftX,
                    'true': rightX,
                    }
            
    def flow_parallel(self, commands):
        commands = [ [psr] if type(psr) is dict else psr for psr in commands]
        return {
                'type': 'parallel',
                'branches': commands            
                }
        pass
    
    def momentum_variable(self, name, var_type='String', default = "''", prompt="'No'", comments = "''", persist = "'No'"):
        return {
                'type': var_type, 
                'params': {'PromptForValue': prompt, 'DefaultValue': default, 'Comments': comments, 'Persist': persist}, 
                'id': name, 
                'containers': []}
    
    def flow_set_dict(self, d):
        '''Sets a set of variables
        
        NOTES
        -----
        Should add a variable testing. A common mistake is to forget the quotes for strings.
        '''
        ret = []
        for key, value in d.iteritems():
            if key in self.variables():
                ret.append(self.flow_set(key, value))
        
        return ret
            