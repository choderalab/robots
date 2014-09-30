"""
Created on 09.05.2014

@author: Jan-Hendrik Prinz
"""

'''
Created on 27.04.2014

@author: JH Prinz
'''

from lxml import etree
import klaatu.util.xmlutil as xp

s = ''

with open('xmlPythonize/test.xmlutil', "r") as myfile:
    s = myfile.read()

# s = s.replace('tecan.at.schema.documents', '')

wr = xp.XMLWrap('analysis')

oo = wr.xml_as_py(s)

root = etree.XML(s)

data = root.xpath('Section{1@Name}[contains(@Name, "")]//Well{}/Scan')

l = list()

for p in data:

    d = p.attrib
    d['text'] = p.text

    for a in data[0].iterancestors():
        d = dict(d, **a.attrib)

    e = {key: d[key] for key in ['Pos', 'WL']}

    l.append(e)

print l[10]

data = root.xpath('Section[contains(@Name, "")]/Data/Well/Scan')

print data[0]

# print(etree.tostring(data[0].getroottree(), pretty_print=True))

# print len(data)

# print oo.keys()

data = oo.get('Section:abs scan/Data/Well*/Scan:480/text', strip=True)

#print data

#obj = oo['TecanMeasurement/MeasurementManualCycle/CyclePlate/PlateRange/Measurement*/Well/MeasurementReading/ReadingLabel/']

#print obj.keys()

#obj['MeasurementFluoInt:top/ReadingFilter:Em/wavelength'] = 3600

#print oo['TecanMeasurement/MeasurementManualCycle/CyclePlate/PlateRange/Measurement*/*']


#print oo['TecanMeasurement/MeasurementManualCycle/CyclePlate/PlateRange/MeasurementF*/Well/MeasurementReading/ReadingLabel/ReadingFilter']
