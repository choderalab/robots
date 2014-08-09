'''
Created on 25.04.2014

@author: jan-hendrikprinz
'''

if __name__ == '__main__':
    pass

from components.momentum.momentum import Parser

from components.containers.containers import Container
import copy


plateData = [
    { 'barcode_id' : 'A', 'label' : 'Corning 3635', 'dropstage' : True, 'size' : '96'},
    { 'barcode_id' : 'B', 'label' : 'Corning 3679', 'dropstage' : True, 'size' : '96'},
    { 'barcode_id' : 'C', 'label' : 'Corning 3651', 'dropstage' : True, 'size' : '96'},
    { 'barcode_id' : 'D', 'label' : '4titude 0223', 'dropstage' : True, 'size' : '96'},
    { 'barcode_id' : 'E', 'label' : 'Corning 3655', 'dropstage' : False, 'size' : '384'},
    { 'barcode_id' : 'F', 'label' : 'Corning 3711', 'dropstage' : False, 'size' : '384'},
    { 'barcode_id' : 'G', 'label' : '4titude 0203', 'dropstage' : False, 'size' : '384'},
     ]

platelist = ['Corning3635', 'Corning3679', 'Corning3651', '4titude0223', 'Corning3655', 'Corning3711', '4titude0203']

Container.connect_mysql()

plateData = [Container.from_id(n) for n in platelist]

plateTypeData = {plate.id_barcode : { 'size' : '"' + plate.plate_type + '"', 'dropstage' : plate.dropstage(), 'label' : '"' + plate.general_name +'"' } for plate in plateData}

print plateTypeData

psr = Parser.readMomentum("PTT Barcode Label.txt")

commands = [ psr.flow_set_dict({
                       'Descriptor' : '"' + plate['label'] + '"', 
                       'PlateType' : '"' + plate['barcode_id'] + '"', 
                       'dropstage' : str(plate['dropstage'])
                       }) for plate in plateData ]

steps = psr['process/steps']
steps[3:6] = []
steps.insert(3, psr.flow_iteration([1,len(commands)], commands))
psr['process/steps'] = steps
psr.toMomentumFile('PTT Barcode Label Plates.txt')

psr = Parser.readMomentum("PTT Barcode Parser.txt")

psr.add_variable('size')    
psr.add_variable('label')    

commands = [ psr.flow_if('PlateType = "' + plateid + '"',psr.flow_set_dict(plate)) for plateid, plate in plateTypeData.iteritems() ]

steps = psr.steps

steps = []
steps.insert(0, psr.flow_parallel(commands))

psr.steps = steps

psr.toMomentumFile('PTT Barcode Parser Full.txt')

cont = Container()
cont.connect()
cont.load_by_name("Corning3569")

print cont.plate_type