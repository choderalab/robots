"""
Created on 25.04.2014

@author: jan-hendrikprinz
"""

from components.momentum.momentum import Momentum
from components.containers.containers import Container

if __name__ == '__main__':

    # List of plates that should be read from the database
    platelist = ['Corning3635', 'Corning3679', 'Corning3651', '4titude0223', 'Corning3655', 'Corning3711', '4titude0203']

    # This so far only works with the database, sorry
    # Container.connect_mysql()
    # plateData = [Container.from_id(n) for n in platelist]

    # Alternatively run this
    plateData = [
        Container(d) for d in
        [
            {'momentum_offsets_high_lidded_lid': u'0', 'plate_material': u'Polystyrene', 'plate_numbering': u'row', 'evo_lid_grip_narrow': u'92', 'manufacturer_url': u'www.corning.com', 'evo_lid_grip_force': u'60', 'id_barcode': u'D',
             'well_distance_y': u'9.00', 'well_diameter_bottom_y': u'6.4', 'well_diameter_bottom_x': u'6.4', 'well_bottom': u'clear', 'manufacturer_number': u'3635', 'momentum_offsets_high_grip_transform': u'Identity',
             'general_id': u'Corning3635', 'id_momentum': u'', 'id': 9L, 'well_profile_anlge': u'0', 'well_volume_working_max': u'200', 'manufacturer_name': u'Corning', 'general_image': u'', 'momentum_offsets_custom_lidded_lid': u'0',
             'well_profile': u'flat', 'well_distance_x': u'9.00', 'general_name_short': u'COR3635', 'plate_rows': u'8', 'momentum_offsets_low_grip_transform': u'Identity', 'stacking_below': u'1', 'id_evo': u'', 'general_comment': u'',
             'plate_height': u'14.22', 'well_diameter_top_x': u'6.9', 'manufacturer_product_url': u'', 'lid_allowed': u'1', 'general_checked': u'1', 'flange_width': u'0', 'plate_color': u'clear', 'well_depth': u'10.7',
             'well_coating': u'none', 'plate_length': u'127.76', 'momentum_offsets_custom_lidded_plate': u'0', 'lid_plate_height': u'16.18', 'well_size': u'full', 'well_volume_working_min': u'75', 'well_position_first_y': u'8.99',
             'well_shape': u'round', 'well_volume_max': u'360', 'well_diameter_top_y': u'6.9', 'momentum_offsets_low_lidded_lid': u'0', 'evo_plate_grip_force': u'75', 'momentum_grip_force': u'75', 'evo_lid_grip_wide': u'135',
             'momentum_offsets_custom_grip_transform': u'Identity', 'stacking_plate_height': u'0', 'general_description': u'Corning 3635 Acrylic Copolymer Flat Bottom 96 Well UV-Transparent Clear Microplate',
             'momentum_offsets_high_lidded_plate': u'0', 'id_infinite': u'', 'manufacturer_pdf_url': u'', 'well_position_first_x': u'12.12', 'plate_sterile': u'1', 'lid_offset': u'0', 'plate_columns': u'12',
             'momentum_offsets_low_lidded_plate': u'0', 'flange_type': u'short', 'stacking_above': u'1', 'plate_width': u'85.48', 'general_name': u'Corning 3635 96 Well UV Clear'},
            {'momentum_offsets_high_lidded_lid': u'0', 'plate_material': u'Polystyrene', 'plate_numbering': u'row', 'evo_lid_grip_narrow': u'92', 'manufacturer_url': u'www.corning.com', 'evo_lid_grip_force': u'60', 'id_barcode': u'C',
             'well_distance_y': u'9.00', 'well_diameter_bottom_y': u'5.0', 'well_diameter_bottom_x': u'5.0', 'well_bottom': u'clear', 'manufacturer_number': u'3679', 'momentum_offsets_high_grip_transform': u'Identity',
             'general_id': u'Corning3679', 'id_momentum': u'5128f0b3-f7c0-45bf-a0fd-697afcd84db7', 'id': 11L, 'well_profile_anlge': u'0', 'well_volume_working_max': u'125', 'manufacturer_name': u'Corning', 'general_image': u'',
             'momentum_offsets_custom_lidded_lid': u'0', 'well_profile': u'flat', 'well_distance_x': u'9.00', 'general_name_short': u'COR3679', 'plate_rows': u'8', 'momentum_offsets_low_grip_transform': u'Identity', 'stacking_below': u'1',
             'id_evo': u'', 'general_comment': u'', 'plate_height': u'14.22', 'well_diameter_top_x': u'4.5', 'manufacturer_product_url': u'', 'lid_allowed': u'1', 'general_checked': u'1', 'flange_width': u'0', 'plate_color': u'clear',
             'well_depth': u'10.5', 'well_coating': u'none', 'plate_length': u'127.76', 'momentum_offsets_custom_lidded_plate': u'0', 'lid_plate_height': u'16.18', 'well_size': u'half', 'well_volume_working_min': u'25',
             'well_position_first_y': u'8.99', 'well_shape': u'round', 'well_volume_max': u'190', 'well_diameter_top_y': u'4.5', 'momentum_offsets_low_lidded_lid': u'0', 'evo_plate_grip_force': u'75', 'momentum_grip_force': u'75',
             'evo_lid_grip_wide': u'135', 'momentum_offsets_custom_grip_transform': u'Identity', 'stacking_plate_height': u'0',
             'general_description': u'Corning 3635 Acrylic Copolymer Flat Bottom 96 Well UV-Transparent Half Clear Microplate', 'momentum_offsets_high_lidded_plate': u'0', 'id_infinite': u'', 'manufacturer_pdf_url': u'',
             'well_position_first_x': u'12.12', 'plate_sterile': u'1', 'lid_offset': u'0', 'plate_columns': u'12', 'momentum_offsets_low_lidded_plate': u'0', 'flange_type': u'short', 'stacking_above': u'1', 'plate_width': u'85.48',
             'general_name': u'Corning 3679 96 Well UV Clear'},
            {'momentum_offsets_high_lidded_lid': u'0', 'plate_material': u'Polystyrene', 'plate_numbering': u'row', 'evo_lid_grip_narrow': u'92', 'manufacturer_url': u'www.corning.com', 'evo_lid_grip_force': u'60', 'id_barcode': u'B',
             'well_distance_y': u'9.00', 'well_diameter_bottom_y': u'6.4', 'well_diameter_bottom_x': u'6.4', 'well_bottom': u'clear', 'manufacturer_number': u'3651', 'momentum_offsets_high_grip_transform': u'Identity',
             'general_id': u'Corning3651', 'id_momentum': u'', 'id': 13L, 'well_profile_anlge': u'0', 'well_volume_working_max': u'200', 'manufacturer_name': u'Corning', 'general_image': u'', 'momentum_offsets_custom_lidded_lid': u'0',
             'well_profile': u'flat', 'well_distance_x': u'9.00', 'general_name_short': u'Corning 3651', 'plate_rows': u'8', 'momentum_offsets_low_grip_transform': u'Identity', 'stacking_below': u'1', 'id_evo': u'', 'general_comment': u'',
             'plate_height': u'14.22', 'well_diameter_top_x': u'6.9', 'manufacturer_product_url': u'', 'lid_allowed': u'1', 'general_checked': u'1', 'flange_width': u'0', 'plate_color': u'black', 'well_depth': u'10.7',
             'well_coating': u'none', 'plate_length': u'127.76', 'momentum_offsets_custom_lidded_plate': u'0', 'lid_plate_height': u'16.18', 'well_size': u'full', 'well_volume_working_min': u'75', 'well_position_first_y': u'8.99',
             'well_shape': u'round', 'well_volume_max': u'Full', 'well_diameter_top_y': u'6.9', 'momentum_offsets_low_lidded_lid': u'0', 'evo_plate_grip_force': u'75', 'momentum_grip_force': u'0', 'evo_lid_grip_wide': u'135',
             'momentum_offsets_custom_grip_transform': u'Identity', 'stacking_plate_height': u'0', 'general_description': u'Corning 3651  Flat Bottom 96 Well Black Clear Bottom', 'momentum_offsets_high_lidded_plate': u'0',
             'id_infinite': u'', 'manufacturer_pdf_url': u'', 'well_position_first_x': u'12.12', 'plate_sterile': u'', 'lid_offset': u'0', 'plate_columns': u'12', 'momentum_offsets_low_lidded_plate': u'0', 'flange_type': u'short',
             'stacking_above': u'1', 'plate_width': u'85.48', 'general_name': u'Corning 3651'},
            {'momentum_offsets_high_lidded_lid': u'0', 'plate_material': u'Polystyrene', 'plate_numbering': u'row', 'evo_lid_grip_narrow': u'92', 'manufacturer_url': u'', 'evo_lid_grip_force': u'60', 'id_barcode': u'A',
             'well_distance_y': u'9.00', 'well_diameter_bottom_y': u'6.30', 'well_diameter_bottom_x': u'6.30', 'well_bottom': u'clear', 'manufacturer_number': u'0223', 'momentum_offsets_high_grip_transform': u'Identity',
             'general_id': u'4titude0223', 'id_momentum': u'bfc20c7b-1941-4814-a13b-3ef0f07b1d3c', 'id': 14L, 'well_profile_anlge': u'0', 'well_volume_working_max': u'200', 'manufacturer_name': u'4titude', 'general_image': u'',
             'momentum_offsets_custom_lidded_lid': u'0', 'well_profile': u'flat', 'well_distance_x': u'9.00', 'general_name_short': u'4ti0223', 'plate_rows': u'8', 'momentum_offsets_low_grip_transform': u'Identity', 'stacking_below': u'1',
             'id_evo': u'', 'general_comment': u'', 'plate_height': u'14.35', 'well_diameter_top_x': u'6.30', 'manufacturer_product_url': u'', 'lid_allowed': u'1', 'general_checked': u'1', 'flange_width': u'0', 'plate_color': u'black',
             'well_depth': u'10.80', 'well_coating': u'none', 'plate_length': u'127.76', 'momentum_offsets_custom_lidded_plate': u'0', 'lid_plate_height': u'0', 'well_size': u'full', 'well_volume_working_min': u'75',
             'well_position_first_y': u'11.24', 'well_shape': u'round', 'well_volume_max': u'', 'well_diameter_top_y': u'6.30', 'momentum_offsets_low_lidded_lid': u'0', 'evo_plate_grip_force': u'75', 'momentum_grip_force': u'75',
             'evo_lid_grip_wide': u'135', 'momentum_offsets_custom_grip_transform': u'Identity', 'stacking_plate_height': u'13.13', 'general_description': u'', 'momentum_offsets_high_lidded_plate': u'0', 'id_infinite': u'',
             'manufacturer_pdf_url': u'', 'well_position_first_x': u'14.38', 'plate_sterile': u'1', 'lid_offset': u'0', 'plate_columns': u'12', 'momentum_offsets_low_lidded_plate': u'0', 'flange_type': u'medium', 'stacking_above': u'1',
             'plate_width': u'85.48', 'general_name': u'4titude 0223 96 Well'},
            {'momentum_offsets_high_lidded_lid': u'0', 'plate_material': u'Polystyrene', 'plate_numbering': u'row', 'evo_lid_grip_narrow': u'92', 'manufacturer_url': u'www.corning.com', 'evo_lid_grip_force': u'60', 'id_barcode': u'G',
             'well_distance_y': u'4.5', 'well_diameter_bottom_y': u'', 'well_diameter_bottom_x': u'', 'well_bottom': u'clear', 'manufacturer_number': u'3655', 'momentum_offsets_high_grip_transform': u'Identity',
             'general_id': u'Corning3655', 'id_momentum': u'', 'id': 1L, 'well_profile_anlge': u'30.0', 'well_volume_working_max': u'80', 'manufacturer_name': u'Corning', 'general_image': u'', 'momentum_offsets_custom_lidded_lid': u'0',
             'well_profile': u'flat', 'well_distance_x': u'4.5', 'general_name_short': u'Corning 3655', 'plate_rows': u'16', 'momentum_offsets_low_grip_transform': u'Identity', 'stacking_below': u'1', 'id_evo': u'', 'general_comment': u'',
             'plate_height': u'14.22', 'well_diameter_top_x': u'3.630', 'manufacturer_product_url': u'', 'lid_allowed': u'1', 'general_checked': u'1', 'flange_width': u'0', 'plate_color': u'black', 'well_depth': u'11.43',
             'well_coating': u'none', 'plate_length': u'127.76', 'momentum_offsets_custom_lidded_plate': u'0', 'lid_plate_height': u'16.18', 'well_size': u'full', 'well_volume_working_min': u'0', 'well_position_first_y': u'8.99',
             'well_shape': u'round', 'well_volume_max': u'Full', 'well_diameter_top_y': u'3.630', 'momentum_offsets_low_lidded_lid': u'0', 'evo_plate_grip_force': u'75', 'momentum_grip_force': u'0', 'evo_lid_grip_wide': u'135',
             'momentum_offsets_custom_grip_transform': u'Identity', 'stacking_plate_height': u'0', 'general_description': u'Corning 3635 Acrylic Copolymer Flat Bottom 96 Well UV-Transparent Half Clear Microplate',
             'momentum_offsets_high_lidded_plate': u'0', 'id_infinite': u'', 'manufacturer_pdf_url': u'', 'well_position_first_x': u'12.12', 'plate_sterile': u'', 'lid_offset': u'0', 'plate_columns': u'24',
             'momentum_offsets_low_lidded_plate': u'0', 'flange_type': u'tall', 'stacking_above': u'1', 'plate_width': u'85.47', 'general_name': u'Corning 3655 384 Well'},
            {'momentum_offsets_high_lidded_lid': u'0', 'plate_material': u'Polystyrene', 'plate_numbering': u'row', 'evo_lid_grip_narrow': u'92', 'manufacturer_url': u'www.corning.com', 'evo_lid_grip_force': u'60', 'id_barcode': u'F',
             'well_distance_y': u'4.5', 'well_diameter_bottom_y': u'3.630', 'well_diameter_bottom_x': u'3.630', 'well_bottom': u'clear', 'manufacturer_number': u'3711', 'momentum_offsets_high_grip_transform': u'Identity',
             'general_id': u'Corning3711', 'id_momentum': u'', 'id': 2L, 'well_profile_anlge': u'30.0', 'well_volume_working_max': u'80', 'manufacturer_name': u'Corning', 'general_image': u'', 'momentum_offsets_custom_lidded_lid': u'0',
             'well_profile': u'flat', 'well_distance_x': u'4.5', 'general_name_short': u'Corning 3711 384 Well Black Clear Bottom', 'plate_rows': u'16', 'momentum_offsets_low_grip_transform': u'Identity', 'stacking_below': u'1',
             'id_evo': u'', 'general_comment': u'', 'plate_height': u'14.22', 'well_diameter_top_x': u'0', 'manufacturer_product_url': u'', 'lid_allowed': u'1', 'general_checked': u'1', 'flange_width': u'0', 'plate_color': u'black',
             'well_depth': u'11.56', 'well_coating': u'none', 'plate_length': u'127.76', 'momentum_offsets_custom_lidded_plate': u'0', 'lid_plate_height': u'16.18', 'well_size': u'full', 'well_volume_working_min': u'20',
             'well_position_first_y': u'8.99', 'well_shape': u'square', 'well_volume_max': u'112', 'well_diameter_top_y': u'0', 'momentum_offsets_low_lidded_lid': u'0', 'evo_plate_grip_force': u'75', 'momentum_grip_force': u'0',
             'evo_lid_grip_wide': u'135', 'momentum_offsets_custom_grip_transform': u'Identity', 'stacking_plate_height': u'0', 'general_description': u'', 'momentum_offsets_high_lidded_plate': u'0', 'id_infinite': u'',
             'manufacturer_pdf_url': u'', 'well_position_first_x': u'12.12', 'plate_sterile': u'', 'lid_offset': u'0', 'plate_columns': u'24', 'momentum_offsets_low_lidded_plate': u'0', 'flange_type': u'tall', 'stacking_above': u'1',
             'plate_width': u'85.48', 'general_name': u'Corning 3711 384 Well '},
            {'momentum_offsets_high_lidded_lid': u'0', 'plate_material': u'Polystyrene', 'plate_numbering': u'row', 'evo_lid_grip_narrow': u'92', 'manufacturer_url': u'', 'evo_lid_grip_force': u'60', 'id_barcode': u'E',
             'well_distance_y': u'4.5', 'well_diameter_bottom_y': u'3.70', 'well_diameter_bottom_x': u'3.70', 'well_bottom': u'clear', 'manufacturer_number': u'0203', 'momentum_offsets_high_grip_transform': u'Identity',
             'general_id': u'4titude0203', 'id_momentum': u'5128f0b3-f7c0-45bf-a0fd-697afcd84db7', 'id': 6L, 'well_profile_anlge': u'0', 'well_volume_working_max': u'0', 'manufacturer_name': u'4titude', 'general_image': u'',
             'momentum_offsets_custom_lidded_lid': u'0', 'well_profile': u'flat', 'well_distance_x': u'4.5', 'general_name_short': u'4ti0203', 'plate_rows': u'16', 'momentum_offsets_low_grip_transform': u'Identity', 'stacking_below': u'1',
             'id_evo': u'', 'general_comment': u'', 'plate_height': u'14.35', 'well_diameter_top_x': u'3.70', 'manufacturer_product_url': u'', 'lid_allowed': u'1', 'general_checked': u'1', 'flange_width': u'0', 'plate_color': u'black',
             'well_depth': u'11.35', 'well_coating': u'none', 'plate_length': u'127.76', 'momentum_offsets_custom_lidded_plate': u'0', 'lid_plate_height': u'0', 'well_size': u'full', 'well_volume_working_min': u'0',
             'well_position_first_y': u'12.13', 'well_shape': u'square', 'well_volume_max': u'0', 'well_diameter_top_y': u'3.70', 'momentum_offsets_low_lidded_lid': u'0', 'evo_plate_grip_force': u'75', 'momentum_grip_force': u'75',
             'evo_lid_grip_wide': u'135', 'momentum_offsets_custom_grip_transform': u'Identity', 'stacking_plate_height': u'13.13', 'general_description': u'4titude 0203 384 Well Black Clear Bottom',
             'momentum_offsets_high_lidded_plate': u'0', 'id_infinite': u'COS384fb', 'manufacturer_pdf_url': u'', 'well_position_first_x': u'8.99', 'plate_sterile': u'1', 'lid_offset': u'0', 'plate_columns': u'24',
             'momentum_offsets_low_lidded_plate': u'0', 'flange_type': u'short', 'stacking_above': u'1', 'plate_width': u'85.48', 'general_name': u'4titude 0203 384 Well '}
        ]
    ]

    plateOrder = [plate.id_barcode for plate in plateData]
    plateOrder.sort()

    ###
    ### BARCODE PRINTING
    ###

    # Read template from momentum
    psr = Momentum.readMomentum("PTT Barcode Label.txt")

    plateTypeData = {plate.id_barcode: {
        'PlateType': '"' + plate.id_barcode + '"',
        'Size': '"' + str(plate.plate_type) + '"',
        'Dropstage': plate.flange_dropstage,
        'Descriptor': '"' + plate.general_name + '"',
        'Bottomread': plate.plate_bottom_read
    } for plate in plateData}

    # Add bottomread as a varible of type Boolean / existing variables are not overwritten
    psr.add_variable('Bottomread', 'Boolean')

    # Add all other variables as type String
    for var in plateTypeData.values()[0]:
        psr.add_variable(var)

    # Create a list of 'set' commands that will set certain variables as given in 
    command_set = [
        psr.flow_set_dict(
            plateTypeData[key]
        )
        for key in plateOrder]

    # Store all but the first 6 steps in 'rest'
    steps = psr.steps
    rest = steps[6:]

    # Clear list of steps
    steps = []

    # Add a comment
    steps.append(psr.flow_comment('project variables'))

    # Set three variables
    steps.append(psr.flow_set('Day', '"21/08/14"'))
    steps.append(psr.flow_set('ProjectID', '"PTTX"'))
    steps.append(psr.flow_set('Descriptor', '"PlateTypeTest"'))

    # Add all set commands iteration dependend    
    steps.append(psr.flow_iteration([1, len(plateOrder)], command_set))
    steps.extend(rest)

    # set the list we just created as the steps or our momentum file
    psr.steps = steps

    # write the current momentum script to new file
    psr.toMomentumFile('PTT Barcode Label Full.txt')


    ###
    ### MOMENTUM SCRIPT THAT SETS PLATE VARIABLES DEPENDING ON PLATE TYPE
    ###

    psr = Momentum.readMomentum("PTT Barcode Parser.txt")

    plateTypeData = {plate.id_barcode: {
        'Size': '"' + str(plate.plate_type) + '"',
        'Dropstage': plate.flange_dropstage,
        'Label': '"' + plate.general_name + '"',
        'Bottomread': plate.plate_bottom_read
    } for plate in plateData}


    # Add bottomread as a varible of type Boolean
    psr.add_variable('Bottomread', 'Boolean')

    # Add all other variables as type String
    for var in plateTypeData.values()[0]:
        psr.add_variable(var)

    command_set = [
        psr.flow_if(
            'PlateType = "' + key + '"',
            psr.flow_set_dict(
                plateTypeData[key]
            )
        )
        for key in plateOrder]

    steps = psr.steps

    # Adjust, so that the initial plate scanning and parsing of the plate type is done
    rest = steps[6:]
    read_barcode = steps[0:3]

    # Clear newly generated plate list
    steps = []

    # Use extend to append several items at once
    steps.extend(read_barcode)

    steps.append(psr.flow_comment('project variables'))
    steps.append(psr.flow_set('Day', '"21/08/14"'))
    steps.append(psr.flow_set('ProjectID', '"PTTX"'))
    steps.append(psr.flow_set('Descriptor', '"PlateTypeTest"'))

    # Add a set of parallel if statements that set plate specific variables according to the platetype in the barcode    
    steps.append(psr.flow_parallel(command_set))
    steps.extend(rest)

    psr.steps = steps
    psr.toMomentumFile('PTT Barcode Parser Full.txt')