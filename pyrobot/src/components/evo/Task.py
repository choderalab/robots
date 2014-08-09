'''
Created on 15.04.2014

@author: jan-hendrikprinz
'''

from util.Units import V
import util.Parser as ps
import re

class Task(object):
    '''
    classdocs
    '''


    def __init__(self, *initial_data, **kwargs):
        
        self.is_source = False
        
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])        
    
class Scheduler(object):
    
    def __init__(self, sources, targets):
        self.sources = sources
        self.targets = targets
    
        # Fast pipetting
        self.do_fast_pipetting = True
        
        # Maximum possible aspiration volume per head
        self.maximum_dispense_level = 900.0
        self.maximum_head_number = 8

        # construct list of consumed solutions (reagents) used
        self.volume_dispenses = dict()
        self.volume_consumed = dict()
        
    def generate(self):
        self.tasks = [
            Task({
                'source' : self.sources[source_index],
                'target' : well,
                'volume' : V(well.volume) * mix
            })
            for plate in self.targets
            for well in plate.targets()
            for (source_index, mix) in enumerate(well.compute_mixing(self.sources))
            if mix > 0.0
        ]
        
        self.tasks = [
            task
            for source in self.sources
            for plate in self.targets
            for task in sorted(self.tasks, key=lambda x: x.target.position[0] * 100 + x.target.position[1])
            if task.target.plate.label == plate.label and task.source.label == source.label
        ]
        
            
    def apply_rule(self, task_rules):
        head_substance = dict()
        
        if type(task_rules) is not list:
            task_rules = [ task_rules ]
    
        for rule in task_rules:
            free_heads = ps._heads_to_list(ps._interprete_heads(rule['head']))
            head_choice = 0;
            for task in self.tasks:
            
                if re.match(rule['source'], task.source.label):
                    pos = task.target.position
                    target_row = pos[0]
                    target_col = pos[1]
                
                    t = rule['assignment']
                    if t == 'row':
                        head = target_row
                    if t == 'col':
                        head = target_col
                    if t == 'free':
                        if task.source.label in head_substance:
                            head = head_substance[task.source.label]
                        else:
                            head = free_heads[head_choice]
                            head_substance[task.source.label] = head
                            head_choice += 1
                            if head_choice == len(free_heads):
                                head_choice = 0
                            
                    task.head = head
                    
                    
    def initialize(self):
        # construct list of consumed solutions (reagents) used
        self.volume_dispenses = dict()
        self.volume_consumed = dict()
        
        for solution in self.sources:
            self.volume_consumed[solution.label] = 0.0
                
        self.dispense_volumes = [ [] for s in range(0, 9) ]
        
        self.loaded_volume = [0.0] * 9
        self.loaded_source = [''] * 9
        
        for task in self.tasks:
            source = task.source
#            destination = task.target
            volume = task.volume.val('u')
            head = task.head
            
            if self.loaded_source[head] == '':
                self.loaded_source[head] = source.label
            
            self.loaded_volume[head] += volume
            if (self.loaded_volume[head] > self.maximum_dispense_level) or (source.label != self.loaded_source[head]):
                self.loaded_source[head] = source.label
                # aspirate as much as possible
                self.dispense_volumes[head].append( self.loaded_volume[head] - volume )
                self.loaded_volume[head] = volume
                                                                    
        for index in range(1,9):
            self.dispense_volumes[index].append( self.loaded_volume[index] )
            self.loaded_volume[index] = 0.0
        
    def write_to_worklist(self, wl):
        
        self.initialize()
        
        dispense_index = [0] * 9
        first_aspirate = True
        
        for task in self.tasks:
            source = task.source
            destination = task.target
            volume = task.volume.val('u')
            head = task.head
        
            if self.do_fast_pipetting:
                if self.loaded_volume[head] < volume:
                    # aspirate as much as possible
                    if self.loaded_volume[head] != 0.0:
                        print "Non empty head washed !!!! Unneccessary"
                        print self.loaded_volume[head]
        
                    self.loaded_volume[head] = 0.0
                    if not first_aspirate:                    
                        wl.washtips()
                    first_aspirate = False
                    
                    possible_volume = self.dispense_volumes[head][dispense_index[head]]
                    dispense_index[head] += 1
                    
                    self.loaded_volume[head] += possible_volume
                                    
                    wl.aspirate(source.plate.label, source.plate.racktype, source.wellID(), possible_volume, head)
        
                wl.dispense(destination.plate.label, destination.plate.racktype, destination.wellID(), volume, head)
                self.loaded_volume[head] -= volume
                self.volume_consumed[source.label] += volume