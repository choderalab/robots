'''
Created on 14.04.2014

@author: jan-hendrikprinz
'''


from util.Units import V

class D300Worklist(object):
    '''
    D300Worklist generator class to construct a worklist string by using standard commands for EVO worklists
    '''

    def __init__(self):
        '''
        Initializes a fresh worklist to be generated
        '''
        
        self.script = ''
        # Number of Aspirations and Dispenses
        self.aspirations = 0
        self.dispenses = 0
        self.washs = 0
        
        self.system_liquid_per_wash = V('7.0ul')

        
    def aspirate(self, RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
        '''
        Aspirate add an aspiration command to the final worklist
        '''
        self.aspirations += 1
        self.script += 'A;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)
    
    def dispense(self, RackLabel, RackType, position, volume, tipmask, LiquidClass='Water free dispense'):
        '''
        Dispense adds a dispense command to the final worklist
        '''
        self.dispenses += 1
        self.script += 'D;%s;;%s;%d;;%f;%s;;%d\r\n' % (RackLabel, RackType, position, volume, LiquidClass, tipmask)
    
    def washtips(self, scheme = 1):
        '''
        Adds a wash command to the script
        '''

        scheme = int(scheme)
        if scheme > 4 or scheme <1:
            # there are only 4 different wash schemes that can be set in the worklist command in evo
            raise ValueError('The specified washing scheme is out of range 1-4.')
        
        self.washs += 1
        self.script += 'W%d;\r\n' % scheme # queue wash tips
    
    def flushliquids(self):
        '''
        Orders the Tecan to dispense of the liquids without a wash.
        '''

        self.script += 'F;\r\n' # flush liquids without washing
    
    def breakexecution(self):
        '''
        Forces the Tecan to finish all pending commands before continuing
        '''
        self.script += 'B;\r\n' # break execution and run all queued commands before continuing
    
    def setDiTi(self, index):
        '''
        Set the Dispensible Tips to be used for dispensing 
        '''
        self.script += 'S;%d;\r\n' % index # set used Dispensiple Tips Index to be used
        
    def decontaminationwash(self):
        '''
        Aspirate add an aspiration command to the final worklist
        '''
        self.script += 'WD;\r\n' # perform a decontamination wash
        
    def comment(self, s):
        '''
        Adds a comment to the worklist file. Comments are completely ignored at runtime
        '''

        self.script += 'C;%s;\r\n' % s # adds a comment that is ignored by EVOware
        
    def used_system_liquid(self):
        return self.system_liquid_per_wash * self.washs