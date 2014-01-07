# Plan ITC experiment.

import itc

from labware import SourcePlate

import units

# Define solvents.
water = Solvent('water')
buffer = Solvent('buffer')

# Define compounds.
nguests = 14 # number of guest compounds
host = Compound('host')
guests = [ Compound(name='guest%02d' % guest_index) for guest_index in range(nguests) ]

# Define troughs on the instrument.
water_trough = SourceTrough(name='water trough', solution=water, volume=100*units.mL, location='1A')
buffer_trough = SourceTrough(name='buffer trough', solution=buffer, volume=100*units.mL, location='1B')

# Define solutions.
host_solution = Solution(compound=host, solvent=buffer, concentration=1.0*units.mM, concentation_uncertainty=0.01*units.mM)
guest_solutions = list()
for guest_index in range(nguests):
    guest_solutions.append( Solution(compound=guests[guest_index], solvent=buffer, concentration=1.0*units.mM, concentration_uncertainty=0.01*units.mM) )

# Define labware.
# NOTE: In practical use, we would have a library of pre-defined labware types.
from labware import SBSLabware
nunc_plate = SBSLabware(
    name='NUNC ITC plate', 
    manufactuerer='Thermo Fisher', 
    catalog_number='260251', 
    wells=96, 
    capacity=1.3*units.mL, 
    color='natural', 
    well_shape='U-shape', 
    description='96 DeepWell-1mL, Sterile', 
    url='http://www.thermoscientific.com/en/product/nunc-1-3-2-0ml-deepwell-plates-shared-wall-technology.html')

# Define source plate for host and guests.
source_plate = SourcePlate(name='source plate', labware=nunc_plate)
source_plate.addWellSequentially(solution=host_soluton, volume=2*units.mL)
for guest_index in range(nguests):
    source_plate.addWellSequentially(solution=guest_solutions[guest_index], volume=1*units.mL)

# Define what we know about affinities.


# Define ITC protocol.
from itc import ITCProtocol
itc_protocol = ITCProtocol()

# Define ITC Experiment.
from itc import ITCExperimentSet, ITCPlate
itc_experiment_set = ITCExperimentSet(name='SAMPL4-CB7 host-guest experiments') # use specified protocol by default
# Add a single plate available for experiments.
itc_experiment_set.addPlate( ITCPlate(name='ITC plate', labware=nunc_plate) )
# Add water control titrations.
for index in range(3):
    itc_experiment_set.addExperiment(syringe=water, cell=water, protocol=itc_protocol)
# Add host-guest experiments.
for index in range(nguests):
    itc_experiment_set.addExperiment(syringe=host_solution, cell=guest_solutions[index], protocol=itc_protocol)
# Add water control titrations.
for index in range(3):
    itc_experiment_set.addExperiment(syringe=water, cell=water, protocol=itc_protocol)

# Check that the experiment can be carried out using available solutions and plates.
# How do we tell it we want to use the liquid LiHa vs air LiHa?
itc_experiment_set.validate()

# Simulate the experiments.
itc_experiment_set.simulate()

# Write Tecan EVO pipetting operations.
worklist_filename = 'itc-setup.worklist'
itc_plate.writeTecanWorklist(worklist_filename)

# Write Auto iTC-200 experiment spreadsheet.
spreadsheet_filename = 'itc-experiment.xls'
itc_plate.writeAutoITCSpreadsheet(spreadsheet_filename)


