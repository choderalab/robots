"""
Created on 14.04.2014

@author: Jan-Hendrik Prinz
"""

from klaatu.components.evo.Plate import Plate

# ##############################################################################
# #  PLATE DEFINITIONS
###############################################################################


source_plate = Plate({
    'name': 'Protein and Buffer',
    'label': 'Source',
    'dimensions': [8, 12],
    'type': '5x3 Vial Holder',
    'maximum_volume': 100,
})

# Destination Plate Definitions


destination_plate_1 = Plate({
    'label': 'Corning3651',
    'type': 'Corning 3651',
    'dimensions': [8, 12],
    'maximum_volume': '200ul'
})

destination_plate_2 = Plate({
    'label': '96well-UVStar',
    'type': '96 Well Microplate',
    'dimensions': [8, 12],
    'maximum_volume': '200ul'
})

destination_plate_3 = Plate({
    'label': 'Corning3679',
    'type': 'Corning 3679',
    'dimensions': [8, 12],
    'maximum_volume': '100ul'
})

destination_plate_4 = Plate({
    'label': '384well',
    'type': '384 Well Plate',
    'dimensions': [16, 24],
    'maximum_volume': '50ul'
})

destination_plate_5 = Plate({
    'label': '384well2',
    'type': '384 Well Plate',
    'dimensions': [16, 24],
    'maximum_volume': '50ul'
})

destination_plate_6 = Plate({
    'label': '384well3',
    'type': '384 Well Plate',
    'dimensions': [16, 24],
    'maximum_volume': '50ul'
})