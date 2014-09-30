"""
Created on 25.04.2014

@author: jan-hendrikprinz
"""

from klaatu.components.containers.containers import Container
import string, glob, re

from lxml import etree
from lxml import objectify

from klaatu.util.xmlutil.XMLWalk import XMLWalker, XPathAnalyzer

if __name__ == '__main__':


    Container.connect_mysql()

    # Container._db.query('TRUNCATE plates')

    filename = 'imports/SMH_Platelist.csv'
    s = ''
    with open(filename, "r") as myfile:
        s = myfile.read()

    lines = s.split('\n')

    first = True
    heads = []

    for line in lines:
        if line[0] != '#':
            if first:
                first = False
                heads = line.split(',')
                hlist = [head for head in heads if head != '']
                hlist.extend(['general_name', 'general_id', 'general_name_short'])
            else:
                input = line.split(',')
                data = dict(zip(heads, input))
                name = data['manufacturer_name'] + ' ' + data['manufacturer_number']
                input = [input[idx] for idx, key in enumerate(heads) if key != '']
                input.extend([name] * 3)
                d = dict(zip(hlist, input))
                if d['plate_wells'] == '96':
                    d['plate_rows'] = 8
                    d['plate_columns'] = 12
                elif d['plate_wells'] == '384':
                    d['plate_rows'] = 16
                    d['plate_columns'] = 24
                elif d['plate_wells'] == '1536':
                    d['plate_rows'] = 32
                    d['plate_columns'] = 48
                else:
                    d['plate_rows'] = 0
                    d['plate_columns'] = 0

                del d['plate_wells']
                c = Container(d)
                c.store(d.keys())

    filename = 'imports/containerTypes.cfg.txt'
    s = etree.tostring(objectify.parse(filename), pretty_print=True)
    s = string.replace(s, '\\', '/')
    s = s.decode('unicode_escape').encode('ascii', 'ignore')

    root = objectify.fromstring(s)

    wk = XMLWalker(root)

    definition = {
        'general_id': '/Name',
        'general_name_short': '/Name',
        'general_name': '/Name',
        'general_description': '/Description',
        'general_image': '/ImagePath',
        'manufacturer_name': '/Manufacturer',
        'manufacturer_url': '/ManufacturerUrl',
        'manufacturer_number': '/PartNumber',
        'manufacturer_product_url': '/ProductInformationUrl',
        'id_momentum': '/Id',
        'plate_height': '/Height',
        'plate_length': '/Length',
        'plate_width': '/Width',
        'stacking_plate_height': '/StackHeight',
        'plate_numbering': '/Numbering',
        'momentum_grip_force': '/GripForce'
    }

    a = '//PlateType?'
    a += '&'.join([key + "='" + value + "/text()'" if value[0] != '@' else key + "='" + value for key, value in definition.iteritems()])

    plates = wk.walk(XPathAnalyzer(a))

    for plate in plates:
        c = Container(plate)
        c.store()

    infiles = glob.glob('imports/*.pdfx')

    for filename in infiles:
        s = etree.tostring(objectify.parse(filename), pretty_print=True)
        #        s = string.replace(s, '\\', '/')
        #s = unicodedata.normalize("NFKD", s.encode('utf8'))
        s = s.encode('ascii', 'ignore').encode('latin-1')

        s = s.decode('utf-8', 'ignore')
        s = s.replace('&#174;', '(R)')
        s = str(s)

        root = objectify.fromstring(s)

        wk = XMLWalker(root)

        res = root.xpath('//ns:DefinitionRectanglePlateBaseDimensions', namespaces={'ns': 'tecan.at.schema.documents'})

        definition = {
            'general_id': '@name',
            'general_name_short': '@name',
            'general_name': '@name',
            'general_comment': '@comment',
            'id_infinite': '@name',
            'manufacturer_name': '@manufacturer',
            'plate_material': '@material',
            'plate_color': '@colordescription',
            'plate_height': 'ns:DefinitionRectanglePlateBaseDimensions/@height',
            'plate_length': 'ns:DefinitionRectanglePlateBaseDimensions/@outsideX',
            'plate_width': 'ns:DefinitionRectanglePlateBaseDimensions/@outsideY',
            'well_position_first_x': 'ns:DefinitionRectanglePlateBaseDimensions/@firstColumnDistanceX',
            'well_position_first_y': 'ns:DefinitionRectanglePlateBaseDimensions/@firstColumnDistanceY',
            'well_position_last_x': 'ns:DefinitionRectanglePlateBaseDimensions/@lastColumnDistanceX',
            'well_position_last_y': 'ns:DefinitionRectanglePlateBaseDimensions/@lastColumnDistanceY',
            'plate_rows': 'ns:DefinitionRectanglePlateBaseDimensions/@nrOfRows',
            'plate_columns': 'ns:DefinitionRectanglePlateBaseDimensions/@nrOfColumns',
            'skirt': 'ns:DefinitionRectanglePlateBaseDimensions/@skirtHeight',
            'lid_plate_height': 'ns:DefinitionRectanglePlateBaseDimensions/@heightWithCover',
            'well_shape': 'ns:DefinitionWellBaseDimensions/@topShape',
            'well_profile': 'ns:DefinitionWellBaseDimensions/@bottomShape',
            'well_diameter_bottom_x': 'ns:DefinitionWellBaseDimensions/@dimensionX',
            'well_diameter_bottom_y': 'ns:DefinitionWellBaseDimensions/@dimensionY',
            'well_depth': 'ns:DefinitionWellBaseDimensions/@dimensionZ',
            'well_volume_max': 'ns:DefinitionWellBaseDimensions/@maxCapacity',
            'well_volume_working_max': 'ns:DefinitionWellBaseDimensions/@maxWorkingCapacity'
        }

        a = '//TecanPlateDefinition?'
        a += '&'.join([key + "='" + value + "/text()'" if '@' not in value else key + "='" + value + "'" for key, value in definition.iteritems()])

        plates = wk.walk(XPathAnalyzer(a, {'ns': 'tecan.at.schema.documents'}))

        d100 = ['plate_height', 'plate_width', 'plate_length', 'well_position', 'well_size', 'well_depth']

        for plate in plates:
            for key, value in plate.iteritems():
                for k in d100:
                    if k in key:
                        if plate[key] != '':
                            plate[key] = str(int(plate[key]) / 1000.0)

            if plate['skirt'] > 7200:
                plate['flange_type'] = 'tall'
            elif plate['skirt'] > 5500:
                plate['flange_type'] = 'medium'
            else:
                plate['flange_type'] = 'short'

            del plate['skirt']

            if int(plate['plate_columns']) > 1:
                plate['well_distance_x'] = (float(plate['well_position_last_x']) - float(plate['well_position_first_x'])) / (int(plate['plate_columns']) - 1.0)
            else:
                plate['well_distance_x'] = 0.0

            if int(plate['plate_rows']) > 1:
                plate['well_distance_y'] = (float(plate['well_position_last_y']) - float(plate['well_position_first_y'])) / (int(plate['plate_rows']) - 1.0)
            else:
                plate['well_distance_y'] = 0.0

            del plate['well_position_last_x']
            del plate['well_position_last_y']

        for plate in plates:
            cm = plate['general_comment']
            if '#' in cm:
                numbers = re.findall('([0-9]+)', cm)
            elif ':' in cm:
                spl = cm.split(':')
                numbers = re.findall('([0-9a-zA-Z]+)', spl[1])
            else:
                numbers = ['0000']

            name = plate['general_name']

            print name, numbers

            for number in numbers:
                if number == '0000':
                    c = Container(plate)
                    c.store()
                elif number != '':
                    plate['manufacturer_number'] = number
                    plate['general_name_short'] = plate['manufacturer_name'].upper() + plate['manufacturer_number']
                    plate['general_name'] = plate['manufacturer_name'] + " " + plate['manufacturer_number'] + " - " + name

                    plate['general_id'] = plate['manufacturer_name'] + " " + plate['manufacturer_number']

                    c = Container(plate)
                    c.store()