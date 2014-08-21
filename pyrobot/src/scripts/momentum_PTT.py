'''
Created on 25.04.2014

@author: jan-hendrikprinz
'''

from components.momentum.momentum import Momentum
from components.containers.containers import Container


if __name__ == '__main__':
    
    platelist = ['Corning3635', 'Corning3679', 'Corning3651', '4titude0223', 'Corning3655', 'Corning3711', '4titude0203']
    
    Container.connect_mysql()    
    plateData = [Container.from_id(n) for n in platelist]
    
    plateTypeData = {plate.id_barcode : { 
             'size' : '"' + str(plate.plate_type) + '"', 
             'dropstage' : plate.flange_dropstage, 
             'label' : '"' + plate.general_name +'"',
             'bottomread' : plate.plate_bottom_read
             } for plate in plateData}
    
    plateOrder = [plate.id_barcode for plate in plateData]    
    plateOrder.sort()
        
    psr = Momentum.readMomentum("PTT Barcode Momentum.txt")

    psr.add_variable('bottomread', 'Boolean')
    for var in plateTypeData.values()[0]:
        psr.add_variable(var)
    
    commands = [ 
                psr.flow_if(
                     'PlateType = "' + key + '"',
                     psr.flow_set_dict(
                        plateTypeData[key]
                    )
                ) 
            for key in plateOrder ]
    
    steps = psr.steps
    
    print psr.containers
    print steps
    
    print psr['profile/id']
    print psr.devices

    steps = []

    psr.add_container('TestPlate', Container.from_id('Corning3635'))

    steps.append(psr.flow_comment('project variables'))
    steps.append(psr.flow_set('Day', '"10/08/14"'))
    steps.append(psr.flow_set('ProjectID', '"PTTX"'))
    steps.append(psr.flow_set('Descriptor', '"PlateTypeTest"'))
    
    steps.append( psr.flow_parallel(commands) )
    
    psr.steps = steps
    
    psr.toMomentumFile('PTT Barcode Momentum Full.txt')