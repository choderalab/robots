'''
Created on 05.05.2014

@author: jan-hendrikprinz
'''

class MomentumFactory(object):
    '''A mixin for Momentum that allows the easy creation of steps for Momentum processes.
    '''
    
    # This might be accessible from the device section of the scripts
    evo_nests = ['red1', 'red2', 'red3', 'red4']
    
    @staticmethod
    def _duration_string(duration):
        '''Format a number of seconds into a duration string
        
        Parameters
        ----------
        duration : int
            Number of seconds to be parsed as a string
        
        Returns
        -------
        s : string
            Duration formatted as a string
        '''
        
        secs = duration % 60
        mins = (duration / 60) % 60
        hours = (duration / 3600) % 24
        
        return "{0:02d}:{0:02d}:{0:02d}".format(secs, mins, hours)
            
    def evo_run_singleplate(self, script, plate_id, start_pos, end_pos):
        '''Construct an EVO Run Command for Momentum Script that uses exactly one plate        
        '''
        return {
                'device': "'EVO'", 
                'action': "'[RunScript]'", 
                'type': "'step'", 
                'containers': [{'lid': "'Unlidded'", 'ends': "'" + end_pos + "'", 'id': "'" + plate_id + "'", 'in': "'" + start_pos + "'"}], 
                'params': {'SetVars': "'No'", 'Enabled': "'Yes'", 'Comments': "''", 'ScriptName': "'" + script + "'", 'RunOnAbortedIteration': "'No'", 'Result': "''", 'Duration': "'00:02:00'", 'MaximumOperationTime': "'00:20:00'"}
                }
        
    def centrifuge_spin(self, plate_id, bucket = 0, duration = '00:00:10', velocity = '500'):
        '''Construct a Spin Command for Momentum Script
        
        Parameters
        ----------
        plate_id : string
            name of the plate to be spun
        bucket : int
            number of the bucket to be used. Either 0 or 1
        duration : mixed
            Either a string of the form `hh:mm:ss` or an integer with the number of seconds. Default is `00:00:10`. 
        velocity : string
            A string containing the velocity in (see Momentum). Default is `500`.
        '''        
        bucket_name = ["'Bucket 1'", "'Bucket 2'"][bucket]
        
        if isinstance( duration, (int, long) ):
            duration = MomentumFactory._duration_string(duration)
        
        return {
                'device': "'HiG4Centrifuge'", 
                'action': "'[Spin]'", 
                'type': "'step'", 
                'containers': [{'id': "'" + plate_id + "'", 'in': bucket_name}], 'params': {'BucketNumberToLoad': bucket_name, 'Enabled': "'Yes'", 'AccelerationPercent': "'50'", 'Comments': "''", 'SpinTimeAtCruiseVelocity': "'" + duration + "'", 'Duration': "'" + duration + "'", 'RunOnAbortedIteration': "'No'", 'Result': "''", 'SpinGs': "'" + velocity + "'", 'DecelerationPercent': "'50'"}}
    
    def flow_if(self, condition, true_steps, false_steps = []):
        '''Construct an if statement
        
        Parameters
        ----------
        condition : string
            a string containing the condition as it would be written in Momentum. Make sure that all the necessary ticks are present for strings, etc.
        true_steps : list
            a list of steps to be performed in case of true
        false:steps : list
            a list of steps to be performed in case of false
            
        Returns
        -------
        step : dict
            a python dict representing the step for the Momentum Script
        '''
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
        '''Construct an set statement
        
        Parameters
        ----------
        variable : string
            name of the variable to be set. Should be either a profile variable or be created in the process
        value : string
            a value for the variable to be set to
        See also
        --------
        Momentum.add_variable()
            
        Returns
        -------
        step : dict
            a python dict representing the step for the Momentum Script
        '''
        return {
                'type': 'set',
                'key': variable,
                'value': value       
                }
        
    def flow_comment(self, s):
        '''Construct a comment statement
        
        Parameters
        ----------
        s : string
            comment to be added
            
        Returns
        -------
        step : dict
            a python dict representing the step for the Momentum Script
        '''
        return {
                'action': 'comment', 
                'type': 'flow',
                'params': {
                    'Comment': "'" + s + "'"
                    }                
                }
        
    def flow_iteration_assign(self, variable, width, values):
        '''Construct an iteration dependent assign block. Depending on a specific iteration a variable is set to a specific value.
        
        Parameters
        ----------
        variable : string
            name of the variable to be set. Should be either a profile variable or be created in the process
            
        width : list of two integers
            A list of shape [min, max] picking the used range for the current scope.
            
        values : list
            a list of values to be set. Item #0 corresponds to the first iteration

        See also
        --------
        flow_iteration()
            
        Returns
        -------
        step : dict
            a python dict representing the step for the Momentum Script
            
        Notes
        -----
        The width should cover all iterations. Since the block uses if statements with greater/less a two small range can have unexpected effects.
        E.g. When [4,5] is picked then the value for 4 is chosen for all instances smaller than 4 also, while 5 is chosen for all iterations beyond 5.
        '''
        return self.flow_iteration(width, [self.flow_set(variable, psr) for psr in range(width[0], width[1] + 1)])
    
    def flow_iteration(self, width, values):
        '''Construct an iteration dependent block. Depending on a specific iteration a block of commands is run.
        
        Parameters
        ----------
        variable : string
            name of the variable to be set. Should be either a profile variable or be created in the process
            
        width : list of two integers
            A list of shape [min, max] picking the used range for the current scope.
            
        values : list
            a list of commands to be run. Item #0 corresponds to the first iteration

        See also
        --------
        flow_iteration_assign()
            
        Returns
        -------
        step : dict
            a python dict representing the step for the Momentum Script
            
        Notes
        -----
        The width should cover all iterations. Since the block uses if statements with greater/less a two small range can have unexpected effects.
        E.g. When [4,5] is picked then the value for 4 is chosen for all instances smaller than 4 also, while 5 is chosen for all iterations beyond 5.
        '''

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
        '''Constructs a parallel block
        
        Parameters
        ----------
        
        commands : list
            Contains blocks of steps that are supposed to be run in parallel.

        Returns
        -------
        step : dict
            a python dict representing the step for the Momentum Script
            
        '''
        commands = [ [psr] if type(psr) is dict else psr for psr in commands]
        return {
                'type': 'parallel',
                'branches': commands            
                }
        pass
    
    def flow_set_dict(self, d):
        '''Sets a set of variables
        
        Returns
        -------
        step : dict
            a python dict representing the step for the Momentum Script            
        
        NOTES
        -----
        Should add a variable type testing. A common mistake is to forget the quotes for strings.
        '''
        ret = []
        for key, value in d.iteritems():
            if key in self.variables():
                ret.append(self.flow_set(key, value))
        
        return ret

    def momentum_variable(self, name, var_type='String', default = "''", prompt="'No'", comments = "''", persist = "'No'"):
        '''Create a python representation for a variable in Momentum Scripts
        
        Parameters
        ----------
        name : string
            Name of the variable as it is used in Momentum.
        var_type : string
            String representing the type of the variable, e.g. `String`, `Date`. Default is `'String'`.
        default : string
            Default value for the variable at initialization. Default is `''`.
        prompt: string
            If Yes Momentum will ask for a value when the process is run. Can be `'Yes'` or `'No'`. Default is `'No'`.
        comments : string
            A comment describing the variable. Default is `''`.
        persis : string
            If Yes the value of the variable will persis. Default is `'No'`.
        
        Returns
        -------
        variable : dict
            a python dict representing the variable for the Momentum Script            
        
        '''
        return {
                'type': var_type, 
                'params': {'PromptForValue': prompt, 'DefaultValue': default, 'Comments': comments, 'Persist': persist}, 
                'id': name, 
                'containers': []}
        
    def momentum_container(self, key, container):
        '''Create a python representaton for a contatiner in Momentum Script
        
        Parameters
        ----------
        key : string
            Name of the container as used in Momentum.
        container : components.container.Container()
            A Container() object has contains all necessary information about the newly created Container
            
        Returns
        -------
        container : dict
            a python dict representing the container for the Momentum Script            
        '''
        
        return {
                'type': 'plate', 
                'params': {
                    'Lid': "'(None)'", 
                    'NumberOfWellRows': "'" + container.plate_rows + "'", 
                    'MoverLiddingGripOffset': "'" + container.lid_offset + "'", 
                    'GripOffset': "'" + container.momentum_offsets_custom_grip_transform + "'", 
                    'ContainerTypeNameId': "'" + container.id_momentum + "'", 
                    'WellNumberingMethod': "'" + container.plate_numbering + "'", 
                    'GripForce': "'" + container.momentum_grip_force + "'", 
                    'BarCodeFile': "''", 
                    'WithLidHeight': "'" + container.lid_plate_height + "'", 
                    'BarCodeAutoExpression': '\'"NC" + Format(Now, "yyMMddHHmmss") + "." + Format(WallClock, "fff")\'', 
                    'Height': "'" + container.plate_height + "'", 
                    'NumberOfWellColumns': "'" + container.plate_columns + "'", 
                    'BarCodeRegularExpression': "''", 
                    'WithLidOffset': "'-5'", 
                    'Attributes': "''", 
                    'StackHeight': "'" + container.stacking_plate_height + "'", 
                    'Thickness': "'" + container.plate_height + "'", 
                    'SetSize': "'1'", 
                    'SealThickness': "'0'"
                    }, 
                'id': key, 
                'containers': []}
